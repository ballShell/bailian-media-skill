# Security

## Secrets

This project reads `DASHSCOPE_API_KEY` from the environment. Never commit API keys, `.env` files, generated request logs that include private media URLs, or downloaded outputs that should not be public.

The CLI does not write the Authorization header to disk.

## Generated URLs

DashScope output URLs may contain temporary signatures. Treat saved response files as sensitive if they include generated media URLs.

## Reporting Issues

If you find a security issue, open a private report through the repository host or contact the maintainer directly.
