from __future__ import annotations


class DockerRunner:
    """Extension point for a future hardened container runner.

    The current release deliberately does not claim application-level Docker
    sandboxing; deployment resource limits live in Compose.
    """

    def run(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError("DockerRunner is not implemented in this release")
