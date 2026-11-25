from dataclasses import dataclass
from pathlib import Path

from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont


def fmt(v: float) -> str:
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("", "-0") else s


@dataclass(frozen=True)
class Face:
    glyphs: object
    cmap: dict[int, str]
    advances: dict[str, int]
    upem: int

    @classmethod
    def load(cls, path: Path) -> "Face":
        font = TTFont(str(path))
        return cls(
            glyphs=font.getGlyphSet(),
            cmap=font.getBestCmap(),
            advances={n: adv for n, (adv, _) in font["hmtx"].metrics.items()},
            upem=font["head"].unitsPerEm,
        )


@dataclass(frozen=True)
class Run:
    face: Face
    text: str
    size: float
    tracking: float = 0.0

    def placements(self) -> tuple[list[tuple[str, float]], float]:
        scale = self.size / self.face.upem
        gap = self.tracking * self.size
        x, out = 0.0, []
        for ch in self.text:
            name = self.face.cmap.get(ord(ch))
            if name is None:
                raise ValueError(f"missing glyph for {ch!r}")
            out.append((name, x))
            x += self.face.advances[name] * scale + gap
        return out, max(0.0, x - gap)

    def width(self) -> float:
        return self.placements()[1]

    def origin(self, x: float, anchor: str) -> float:
        width = self.width()
        return {"start": x, "middle": x - width / 2, "end": x - width}[anchor]

    def draw(self, pen, x: float, y: float, anchor: str = "start") -> None:
        placed, _ = self.placements()
        start = self.origin(x, anchor)
        scale = self.size / self.face.upem
        for name, dx in placed:
            self.face.glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, start + dx, y)))

    def path(self, x: float, y: float, anchor: str = "start") -> str:
        pen = SVGPathPen(self.face.glyphs, ntos=fmt)
        self.draw(pen, x, y, anchor)
        return pen.getCommands()

    def bounds(self, x: float, y: float, anchor: str = "start") -> tuple[float, float, float, float]:
        pen = BoundsPen(self.face.glyphs)
        self.draw(pen, x, y, anchor)
        return pen.bounds
