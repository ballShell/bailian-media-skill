#!/usr/bin/env python3
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

TOOL_DIR = Path(__file__).resolve().parent
CONFIG_PATH = TOOL_DIR / "models.json"


class BailianError(Exception):
    pass


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def expand(path):
    return Path(os.path.expanduser(path)).resolve()


def read_json_arg(value):
    if not value:
        return {}
    if value.startswith("@"):
        return json.loads(Path(value[1:]).read_text(encoding="utf-8"))
    return json.loads(value)


def http_json(method, url, api_key, payload=None, timeout=60, async_request=False):
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")
    if payload is not None and async_request:
        req.add_header("X-DashScope-Async", "enable")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise BailianError(f"HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise BailianError(f"Network error: {exc}") from exc


def is_remote_url(value):
    parsed = urllib.parse.urlparse(value or "")
    return parsed.scheme in {"http", "https", "oss"}


def require_remote_media(media):
    for item in media:
        url = item.get("url")
        if url and not is_remote_url(url):
            raise BailianError(
                f"Local media is not directly uploadable yet: {url}. "
                "Upload it to OSS or another reachable URL, then pass that URL."
            )


def choose_models(config, capability, requested):
    models = config["models"]
    if not requested or requested == ["auto"]:
        requested = config["capability_defaults"][capability]
    result = []
    for name in requested:
        if name not in models:
            raise BailianError(f"Unknown model: {name}")
        if capability not in models[name]["capabilities"]:
            raise BailianError(f"Model {name} does not support {capability}")
        result.append(name)
    return result


def messages_input(prompt, media):
    content = []
    for item in media:
        media_type = item.get("type", "image")
        key = "image" if media_type not in {"video", "base"} else "video"
        content.append({key: item["url"]})
    content.append({"text": prompt})
    return {"messages": [{"role": "user", "content": content}]}


def video_input(prompt, media):
    payload = {"prompt": prompt}
    if media:
        payload["media"] = media
    return payload


def build_payload(model_name, model_meta, capability, prompt, media, parameters):
    params = dict(model_meta.get("default_parameters", {}))
    params.update(parameters)
    if model_meta["request_style"] == "messages":
        input_payload = messages_input(prompt, media)
    else:
        input_payload = video_input(prompt, media)
    return {"model": model_name, "input": input_payload, "parameters": params}


def task_id_from(response):
    output = response.get("output") or {}
    return response.get("task_id") or output.get("task_id")


def task_status(response):
    output = response.get("output") or {}
    status = output.get("task_status") or response.get("task_status") or output.get("status") or response.get("status")
    return (status or "UNKNOWN").upper()


def wait_task(base_url, task_id, api_key, poll_interval, timeout_sec):
    deadline = time.time() + timeout_sec
    task_url = base_url.rstrip("/") + f"/tasks/{task_id}"
    last = {}
    while time.time() < deadline:
        last = http_json("GET", task_url, api_key, timeout=60)
        status = task_status(last)
        if status in {"SUCCEEDED", "SUCCESS", "COMPLETED"}:
            return last
        if status in {"FAILED", "CANCELED", "CANCELLED"}:
            raise BailianError(f"Task {task_id} ended with {status}: {json.dumps(last, ensure_ascii=False)}")
        time.sleep(poll_interval)
    raise BailianError(f"Task {task_id} timed out after {timeout_sec}s. Last response: {json.dumps(last, ensure_ascii=False)}")


def collect_urls(value):
    found = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key in {"url", "image", "video_url", "video"} and isinstance(item, str) and is_remote_url(item):
                found.append(item)
            else:
                found.extend(collect_urls(item))
    elif isinstance(value, list):
        for item in value:
            found.extend(collect_urls(item))
    return found


def guess_ext(url, content_type=None):
    path = urllib.parse.urlparse(url).path.lower()
    for ext in [".png", ".jpg", ".jpeg", ".webp", ".mp4", ".mov"]:
        if path.endswith(ext):
            return ext
    if content_type:
        if "png" in content_type:
            return ".png"
        if "jpeg" in content_type:
            return ".jpg"
        if "webp" in content_type:
            return ".webp"
        if "mp4" in content_type:
            return ".mp4"
    return ".bin"


def download_outputs(urls, out_dir, prefix):
    outputs = []
    for index, url in enumerate(dict.fromkeys(urls), start=1):
        try:
            with urllib.request.urlopen(url, timeout=180) as resp:
                content_type = resp.headers.get("Content-Type", "")
                ext = guess_ext(url, content_type)
                local_path = out_dir / f"{prefix}-{index}{ext}"
                local_path.write_bytes(resp.read())
            kind = "video" if ext in {".mp4", ".mov"} else "image"
            outputs.append({"type": kind, "url": url, "local_path": str(local_path)})
        except Exception as exc:
            outputs.append({"type": "unknown", "url": url, "download_error": str(exc)})
    return outputs


def run_capability(args):
    config = load_config()
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    if not api_key:
        raise BailianError("Missing environment variable DASHSCOPE_API_KEY")

    base_url = args.base_url or os.environ.get("DASHSCOPE_BASE_URL") or config["defaults"]["base_url"]
    output_root = expand(args.output_root or os.environ.get("BAILIAN_MEDIA_OUTPUT_ROOT") or config["defaults"]["output_root"])
    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = output_root / args.capability.replace("_", "-") / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    media = read_json_arg(args.media)
    if isinstance(media, dict):
        media = [media]
    if media is None:
        media = []
    require_remote_media(media)

    parameters = read_json_arg(args.parameters)
    selected = choose_models(config, args.capability, args.models)
    results = []

    for model_name in selected:
        model_meta = config["models"][model_name]
        model_dir = run_dir / model_name.replace("/", "__")
        model_dir.mkdir(parents=True, exist_ok=True)
        payload = build_payload(model_name, model_meta, args.capability, args.prompt, media, parameters)
        (model_dir / "request.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        create_url = base_url.rstrip("/") + model_meta["endpoint"]
        result = {"ok": False, "model": model_name, "capability": args.capability, "output_dir": str(model_dir)}
        try:
            create_response = http_json(
                "POST",
                create_url,
                api_key,
                payload,
                timeout=90,
                async_request=model_meta.get("async_only", True),
            )
            (model_dir / "create-response.json").write_text(json.dumps(create_response, ensure_ascii=False, indent=2), encoding="utf-8")
            task_id = task_id_from(create_response)
            final_response = create_response
            if args.wait and task_id:
                final_response = wait_task(
                    base_url,
                    task_id,
                    api_key,
                    args.poll_interval or config["defaults"]["poll_interval_sec"],
                    args.timeout or config["defaults"]["timeout_sec"],
                )
                (model_dir / "final-response.json").write_text(json.dumps(final_response, ensure_ascii=False, indent=2), encoding="utf-8")
            urls = collect_urls(final_response)
            outputs = download_outputs(urls, model_dir, "result") if args.download else [{"url": url} for url in urls]
            result.update({"ok": True, "task_id": task_id, "outputs": outputs, "raw_response_path": str(model_dir / ("final-response.json" if args.wait and task_id else "create-response.json"))})
        except Exception as exc:
            result.update({"error": str(exc)})
            (model_dir / "error.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        results.append(result)

    summary = {"ok": any(item["ok"] for item in results), "run_dir": str(run_dir), "capability": args.capability, "results": results}
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["ok"] else 1


def list_models(args):
    config = load_config()
    rows = []
    for name, meta in sorted(config["models"].items()):
        if args.capability and args.capability not in meta["capabilities"]:
            continue
        rows.append({"model": name, "family": meta["family"], "capabilities": meta["capabilities"], "note": meta.get("region_note")})
    print(json.dumps(rows, ensure_ascii=False, indent=2))
    return 0


def add_capability_parser(subparsers, command, capability):
    parser = subparsers.add_parser(command)
    parser.set_defaults(func=run_capability, capability=capability)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--models", nargs="+", default=["auto"], help="Use auto or one/more explicit model IDs")
    parser.add_argument("--media", default="[]", help="JSON array/object or @file. URLs only for now.")
    parser.add_argument("--parameters", default="{}", help="JSON object or @file")
    parser.add_argument("--base-url")
    parser.add_argument("--output-root")
    parser.add_argument("--wait", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--download", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--timeout", type=int)
    parser.add_argument("--poll-interval", type=int)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="bailian-media")
    subparsers = parser.add_subparsers(required=True)
    add_capability_parser(subparsers, "text-to-image", "text_to_image")
    add_capability_parser(subparsers, "image-edit", "image_edit")
    add_capability_parser(subparsers, "text-to-video", "text_to_video")
    add_capability_parser(subparsers, "image-to-video", "image_to_video")
    add_capability_parser(subparsers, "reference-to-video", "reference_to_video")
    add_capability_parser(subparsers, "video-edit", "video_edit")
    list_parser = subparsers.add_parser("list-models")
    list_parser.add_argument("--capability", choices=["text_to_image", "image_edit", "text_to_video", "image_to_video", "reference_to_video", "video_edit"])
    list_parser.set_defaults(func=list_models)
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except BailianError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
