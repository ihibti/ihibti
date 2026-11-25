import pytest

from profile_card.typeset import Face, Run

stub = Face(glyphs=None, cmap={65: "A", 66: "B"}, advances={"A": 500, "B": 700}, upem=1000)


def test_width_adds_tracking_between_glyphs_not_after_the_last():
    placed, width = Run(stub, "AB", size=10, tracking=0.1).placements()
    assert placed == [("A", 0.0), ("B", 6.0)]
    assert width == 13.0


def test_origin_follows_the_anchor():
    run = Run(stub, "AB", size=10, tracking=0.1)
    assert [run.origin(100, a) for a in ("start", "middle", "end")] == [100, 93.5, 87]


def test_missing_glyph_raises():
    with pytest.raises(ValueError, match="missing glyph for 'Z'"):
        Run(stub, "AZ", size=10).placements()
