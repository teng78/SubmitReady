# SubmitReady examples

`rules/` contains immutable built-in rule examples for C, C++, and Python.
`projects/` contains readable source fixtures. Run `python scripts/generate_examples.py`
to create deterministic ZIP files in `examples/generated/`, including
`zip-slip.zip`, whose `../escaped.txt` entry must be rejected.

All credential-like values are unmistakably fake test data. Do not reuse them.
