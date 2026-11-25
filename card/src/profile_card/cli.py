import argparse
from pathlib import Path

from .spec import load
from .svg import assets
from .typeset import Face


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


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="profile-card")
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("assets", help="write card.svg, signature-light.svg and signature-dark.svg")
    generate.add_argument("--spec", type=Path, required=True)
    generate.add_argument("--fonts", type=Path, required=True)
    generate.add_argument("--out", type=Path, required=True)
    generate.set_defaults(run=lambda args: write_assets(args.spec, args.fonts, args.out))
    args = parser.parse_args(argv)
    args.run(args)


if __name__ == "__main__":
    main()
