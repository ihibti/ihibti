import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Line:
    text: str
    size: float
    tracking: float
    x: float
    y: float
    anchor: str


@dataclass(frozen=True)
class Card:
    width: int
    height: int
    offset: tuple[int, int]
    bottom: int
    stock: str
    ink: str
    font: str
    size_scale: float
    watermark_font: str
    alt: str
    watermark: Line
    lines: tuple[Line, ...]


@dataclass(frozen=True)
class Signature:
    text: str
    font: str
    size: float
    pad: float
    light: str
    dark: str


@dataclass(frozen=True)
class Spec:
    card: Card
    signature: Signature


def parse(text: str) -> Spec:
    data = tomllib.loads(text)
    card = data["card"]
    return Spec(
        card=Card(
            **{
                **card,
                "offset": tuple(card["offset"]),
                "watermark": Line(**card["watermark"]),
                "lines": tuple(Line(**line) for line in card["lines"]),
            }
        ),
        signature=Signature(**data["signature"]),
    )


def load(path: Path) -> Spec:
    return parse(path.read_text(encoding="utf-8"))
