import argparse
import json
import subprocess
from pathlib import Path

from .preview import localize, page
from .spec import load
from .svg import assets
from .typeset import Face

CONTEXT = "ihibti/ihibti"


def write_assets(spec_path: Path, fonts: Path, out: Path) -> None:
    spec = load(spec_path)
    files = assets(
        spec,
        Face.load(fonts / spec.card.font),
        Face.load(fonts / spec.card.watermark_font),
        Face.load(fonts / spec.signature.font),
    )
    out.mkdir(parents=True, exist_ok=True)
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")


def render_markdown(text: str) -> str:
    body = json.dumps({"text": text, "mode": "gfm", "context": CONTEXT})
    return subprocess.run(
        ["gh", "api", "markdown", "--input", "-"], input=body, check=True, capture_output=True, text=True
    ).stdout


def write_preview(readme: Path, assets_dir: Path, out: Path) -> None:
    base = readme.resolve().parent
    files = {
        svg.resolve().relative_to(base).as_posix(): svg.read_text(encoding="utf-8")
        for svg in sorted(assets_dir.glob("*.svg"))
    }
    rendered = render_markdown(readme.read_text(encoding="utf-8"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page(localize(rendered, files, dark=False), localize(rendered, files, dark=True)), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="profile-card")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("assets", help="write card.svg, signature-light.svg and signature-dark.svg")
    generate.add_argument("--spec", type=Path, required=True)
    generate.add_argument("--fonts", type=Path, required=True)
    generate.add_argument("--out", type=Path, required=True)
    generate.set_defaults(run=lambda args: write_assets(args.spec, args.fonts, args.out))
    preview = commands.add_parser("preview", help="render the README through GitHub in light, dark and phone panes")
    preview.add_argument("--readme", type=Path, required=True)
    preview.add_argument("--assets", type=Path, required=True)
    preview.add_argument("--out", type=Path, required=True)
    preview.set_defaults(run=lambda args: write_preview(args.readme, args.assets, args.out))
    args = parser.parse_args(argv)
    args.run(args)


if __name__ == "__main__":
    main()
