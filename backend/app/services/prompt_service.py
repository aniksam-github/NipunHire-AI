"""Feature-agnostic loading and rendering of Markdown prompt templates."""

from functools import lru_cache
from pathlib import Path


PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


class PromptNotFoundError(FileNotFoundError):
    """Raised when the caller requests a prompt template that does not exist."""


def _prompt_path(name: str) -> Path:
    if Path(name).name != name or Path(name).suffix:
        raise PromptNotFoundError(f"Prompt template not found: {name!r}")
    return PROMPTS_DIR / f"{name}.md"


@lru_cache(maxsize=None)
def _read_template(name: str, modified_at_ns: int) -> str:
    """Cache content by mtime; an edited template receives a new cache key."""
    return _prompt_path(name).read_text(encoding="utf-8")


def load_prompt(name: str, /, **variables: object) -> str:
    """Load a named Markdown template and render its ``{variable}`` placeholders.

    File content is cached in memory. A lightweight mtime check on each call
    invalidates the cache after a template edit, preventing stale prompt text.
    """
    path = _prompt_path(name)
    try:
        template = _read_template(name, path.stat().st_mtime_ns)
    except FileNotFoundError as exc:
        raise PromptNotFoundError(f"Prompt template not found: {name!r}") from exc
    return template.format(**variables)
