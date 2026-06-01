# Contributing

Contributions are welcome.

## Development Checks

Run:

```bash
python3 -m py_compile tools/bailian-media/bailian_media.py
python3 -m json.tool tools/bailian-media/models.json >/dev/null
./tools/bailian-media/bailian-media list-models
```

Avoid adding runtime dependencies unless they are clearly necessary.

## Model Registry

Model metadata lives in `tools/bailian-media/models.json`. Keep request formatting in the Python CLI and capability/model selection in the registry.

## Do Not Commit

- API keys
- `.env`
- generated outputs
- temporary response files with signed media URLs
