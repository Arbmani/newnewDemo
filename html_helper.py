# template_renderer.py
from pathlib import Path
import pulumi

TEMPLATE_DIR = Path(__file__).parent / "templates"

def get_template(template_name: str = "a") -> pulumi.Output[str]:
    template_path = TEMPLATE_DIR / f"{template_name}.html"
    if not template_path.exists():
        raise FileNotFoundError(
            f"Template not found: {template_path}. "
        )

    return pulumi.Output.from_input(template_path.read_text(encoding="utf-8"))
