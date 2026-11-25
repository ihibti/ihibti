import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from profile_card.spec import load
from profile_card.svg import card_svg, signature_svg
from profile_card.typeset import Face

CARD_DIR = Path(__file__).resolve().parents[1]
FONTS = CARD_DIR / "fonts"
SPEC_PATH = CARD_DIR / "card.toml"
NS = "{http://www.w3.org/2000/svg}"


@pytest.fixture(scope="module")
def spec():
    return load(SPEC_PATH)


def parse_self_contained(out: str) -> ET.Element:
    root = ET.fromstring(out)
    assert root.tag == f"{NS}svg"
    assert root.get("role") == "img"
    assert not list(root.iter(f"{NS}text"))
    assert "@font-face" not in out
    assert set(re.findall(r'https?://[^"\'\s)]+', out)) == {"http://www.w3.org/2000/svg"}
    return root


def test_card_is_self_contained(spec):
    out = card_svg(spec, Face.load(FONTS / spec.card.font), Face.load(FONTS / spec.card.watermark_font))
    root = parse_self_contained(out)
    assert root.find(f"{NS}title").text == spec.card.alt
    assert root.get("viewBox") == "0 0 1130 700"


def test_signature_is_self_contained(spec):
    out = signature_svg(spec, Face.load(FONTS / spec.signature.font), spec.signature.light)
    root = parse_self_contained(out)
    assert root.get("viewBox").startswith("0 0 ")


def test_generation_is_deterministic(tmp_path):
    outs = [tmp_path / "a", tmp_path / "b"]
    for seed, out in zip(("0", "1"), outs):
        subprocess.run(
            [sys.executable, "-m", "profile_card.cli", "assets", "--spec", str(SPEC_PATH), "--fonts", str(FONTS), "--out", str(out)],
            check=True,
            env={**os.environ, "PYTHONHASHSEED": seed},
        )
    names = sorted(p.name for p in outs[0].iterdir())
    assert names == ["card.svg", "signature-dark.svg", "signature-light.svg"]
    for name in names:
        assert (outs[0] / name).read_bytes() == (outs[1] / name).read_bytes(), name
