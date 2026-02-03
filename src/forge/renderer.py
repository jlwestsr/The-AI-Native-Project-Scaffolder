"""Jinja2 template rendering for Forge profiles."""
from __future__ import annotations

import hashlib
from pathlib import Path

from jinja2 import Environment, BaseLoader, TemplateNotFound

from forge.models import ResolvedProfile, RenderedFile


class ProfileTemplateLoader(BaseLoader):
    """Jinja2 loader that searches template_dirs in order (child first)."""

    def __init__(self, template_dirs: list[Path]) -> None:
        self.template_dirs = template_dirs

    def get_source(
        self, environment: Environment, template: str
    ) -> tuple[str, str, callable]:
        for tpl_dir in self.template_dirs:
            path = tpl_dir / template
            if path.is_file():
                source = path.read_text(encoding="utf-8")
                return source, str(path), lambda: path.stat().st_mtime
        raise TemplateNotFound(template)


def render_templates(
    profile: ResolvedProfile, variables: dict
) -> list[RenderedFile]:
    """Render all templates in a profile to in-memory RenderedFile objects.

    Args:
        profile: A fully resolved profile (inheritance already merged).
        variables: User-provided template variables.

    Returns:
        List of RenderedFile objects, one per file in the profile.

    Raises:
        FileNotFoundError: If a template cannot be found in any template dir.
    """
    env = Environment(
        loader=ProfileTemplateLoader(profile.template_dirs),
        keep_trailing_newline=True,
    )

    rendered: list[RenderedFile] = []

    for output_path, template_name in profile.files.items():
        # Check conditionals
        condition_var = profile.conditionals.get(output_path)
        if condition_var is not None and not variables.get(condition_var):
            continue

        # Render output path (may contain Jinja2 variables)
        resolved_output_path = env.from_string(output_path).render(**variables)

        # Render template content
        try:
            template = env.get_template(template_name)
        except TemplateNotFound:
            raise FileNotFoundError(
                f"Template '{template_name}' not found in: "
                f"{[str(d) for d in profile.template_dirs]}"
            )

        content = template.render(**variables)
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]

        rendered.append(
            RenderedFile(
                output_path=resolved_output_path,
                content=content,
                template_name=template_name,
                content_hash=content_hash,
            )
        )

    return rendered
