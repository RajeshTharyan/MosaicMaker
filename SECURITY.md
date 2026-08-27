# Security

The Streamlit UI **accepts image uploads**. Treat any deployment as an untrusted input surface.

## What the app does with files

- Uploads are read in memory with Pillow and composed into a PNG held in Streamlit `session_state`.
- The application code does not write uploads to disk and does not fetch remote URLs.
- There is no login, quota, or virus scan.

## Deploying a copy

- Do not point a public instance at confidential figures. Anyone who can open the app can upload content into that process’s memory.
- Large or many TIFFs can exhaust RAM and CPU on a shared host. Bound instance size or keep the app private.
- Streamlit secrets belong in `.streamlit/secrets.toml`, which is gitignored. This app does not currently require secrets.

## Reporting a vulnerability

Please **do not** open a public issue for a security problem.

Email **rajeshtharyan@gmail.com** with steps to reproduce, the affected revision, and impact. GitHub’s private [security advisory](https://github.com/RajeshTharyan/MosaicMaker/security/advisories/new) form is also fine if you prefer.
