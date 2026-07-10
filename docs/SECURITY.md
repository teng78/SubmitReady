# Security model

## Trust boundaries

Uploaded ZIPs, their filenames and bytes, custom YAML rules, stored report text and subprocess output
are untrusted. The browser is not a command authority. The host environment may contain credentials
that must never reach a child process, response or log.

## Implemented controls

- Upload and extraction limits cover archive bytes, entry count and expanded bytes.
- Extraction rejects absolute, drive, UNC and traversal paths; links, special entries, duplicate
  normalized names and corrupt archives fail closed.
- Rules reject unknown fields, path traversal, shell metacharacters, dangerous executables and
  language-incompatible commands.
- Commands use validated argument arrays with `shell=False`; timeout, output truncation and an
  environment allowlist are mandatory. API keys are not inherited.
- Sensitive scanning detects common credential patterns, private-key headers, dotenv files and
  obvious password assignment. Evidence is redacted.
- Runtime data, databases, uploads and `.env` files are ignored by Git. CI runs
  `python scripts/security_scan.py` against tracked production files.
- Containers run without root, capabilities or privilege escalation and have CPU, memory and process
  limits. Only the data volume and temporary directories are writable.

## Important limitations

The controlled subprocess runner is **not an adversarial sandbox**. Its allowlist, process controls and
workspace reduce mistakes but do not eliminate compiler/interpreter escapes, kernel attacks, local
network access or denial of service. Untrusted execution is therefore disabled by default. Only enable
it for code you trust, preferably on a disposable machine. The `network_disabled` rule flag cannot be
fully enforced by the local subprocess fallback.

The Compose backend needs an application network so nginx can reach it; this is not the same as a
per-run network-isolated Docker runner. A future DockerRunner should create a fresh container per run
with no network, read-only root filesystem, non-root UID, tight cgroup limits and guaranteed cleanup.

## Credentials

The shipped application has no paid provider and does not need an API key. `.env.example` contains
only non-secret configuration. Do not add real keys to `.env`, Git, test fixtures, rule files, logs or
frontend variables. If an external AI provider is added later, use OS keyring/container secrets,
display only configured/not-configured status, and send only redacted truncated diagnostics.

## Reporting a vulnerability

Do not include a live credential or private student submission in an issue. Provide a minimal synthetic
reproduction and the affected version privately to the repository owner or course staff.
