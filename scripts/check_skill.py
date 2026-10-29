"""Validate the MVP package; requires PyYAML 6.0.3 in the development environment."""
import json
from pathlib import Path
import re
import yaml


def main():
    root = Path(__file__).resolve().parents[1]
    package = root / "skills/ecommerce-image-replicator"
    text = (package / "SKILL.md").read_text(encoding="utf-8")
    _, front, body = text.split("---", 2)
    data = yaml.safe_load(front)
    assert data["name"] == package.name
    assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["name"])
    assert isinstance(data["description"], str) and 0 < len(data["description"]) <= 1024
    assert len(body.splitlines()) <= 500
    for target in re.findall(r"\]\(([^)]+)\)", body):
        assert not Path(target).is_absolute() and ".." not in Path(target).parts
        assert (package / target.split("#")[0]).is_file()
    assert not list(package.rglob(".env"))
    report = {"status": "passed", "name": data["name"],
        "description_characters": len(data["description"]), "body_lines": len(body.splitlines()),
        "scope": "structure only; no skill discovery or behavioral acceptance"}
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
