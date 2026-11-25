import base64
import re

from profile_card.preview import localize, page

VIDEO_UUID = "7c3de487-aca8-4667-bbb7-c9f742d86ae1"
IMAGE_UUID = "0a1b2c3d-4e5f-4a6b-8c7d-9e0f1a2b3c4d"
PRIVATE = "https://private-user-images.githubusercontent.com/141340433"

RENDERED = f"""<p align="center"><a href="https://www.linkedin.com/in/ismael-hibti/"><img src="assets/card.svg" width="620" alt="card" style="max-width: 100%;"></a></p>
<video src="{PRIVATE}/563458105-{VIDEO_UUID}.webm?jwt=abc.def" data-canonical-src="{PRIVATE}/563458105-{VIDEO_UUID}.webm?jwt=abc.def" controls="controls" muted="muted"></video>
<img src="{PRIVATE}/563458106-{IMAGE_UUID}.png?jwt=ghi" alt="other">
<picture>
<source media="(prefers-color-scheme: dark)" srcset="assets/signature-dark.svg">
<img src="assets/signature-light.svg" height="52" alt="Ismael">
</picture>"""

ASSETS = {
    "assets/card.svg": "<svg>card</svg>",
    "assets/signature-light.svg": "<svg>light</svg>",
    "assets/signature-dark.svg": "<svg>dark</svg>",
}


def data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def test_localize_inlines_assets_and_picks_the_theme():
    for dark, media in ((True, "all"), (False, "not all")):
        out = localize(RENDERED, ASSETS, dark=dark)
        assert '="assets/' not in out
        assert f'<img src="{data_uri("<svg>card</svg>")}" width="620"' in out
        assert f'srcset="{data_uri("<svg>dark</svg>")}"' in out
        assert f'<img src="{data_uri("<svg>light</svg>")}" height="52"' in out
        assert f'<source media="{media}" srcset=' in out
        assert "private-user-images" not in out
        assert out.count(f'="https://github.com/user-attachments/assets/{VIDEO_UUID}"') == 2
        assert out.count(f'="https://github.com/user-attachments/assets/{IMAGE_UUID}"') == 1


def test_page_frames_light_dark_and_phone():
    out = page('<p title="a">light</p>', "<p>dark</p>")
    frames = re.findall(r"<iframe [^>]*>", out)
    assert [re.search(r'width="(\d+)"', f)[1] for f in frames] == ["896", "896", "390"]
    assert ["github-markdown-light.css" in f for f in frames] == [True, False, True]
    assert ["github-markdown-dark.css" in f for f in frames] == [False, True, False]
    assert ["&lt;p title=&quot;a&quot;&gt;light&lt;/p&gt;" in f for f in frames] == [True, False, True]
    assert ["&lt;p&gt;dark&lt;/p&gt;" in f for f in frames] == [False, True, False]
