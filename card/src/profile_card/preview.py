import base64
import html as markup
import re

REFERENCE = re.compile(r'\b(src|srcset)="([^"]*)"')
DARK_SOURCE = 'media="(prefers-color-scheme: dark)"'
PRIVATE_ATTACHMENT = re.compile(
    r"https://private-user-images\.githubusercontent\.com/\d+/\d+-"
    r"([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.\w+\?[^\"]*"
)
CSS = "https://cdn.jsdelivr.net/npm/github-markdown-css@5/github-markdown-{theme}.css"
THEMES = {
    "light": {"background": "#ffffff", "border": "#d1d9e0"},
    "dark": {"background": "#0d1117", "border": "#3d444d"},
}
PANES = (
    {"label": "Light, desktop", "theme": "light", "width": 896, "outer": 0, "inner": 24},
    {"label": "Dark, desktop", "theme": "dark", "width": 896, "outer": 0, "inner": 24},
    {"label": "Light, phone", "theme": "light", "width": 390, "outer": 16, "inner": 16},
)


def data_uri(svg: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def localize(html: str, assets: dict[str, str], dark: bool) -> str:
    inlined = REFERENCE.sub(lambda m: f'{m[1]}="{data_uri(assets[m[2]])}"' if m[2] in assets else m[0], html)
    themed = inlined.replace(DARK_SOURCE, f'media="{"all" if dark else "not all"}"')
    return PRIVATE_ATTACHMENT.sub(r"https://github.com/user-attachments/assets/\1", themed)


def frame(body: str, theme: str, outer: int, inner: int) -> str:
    colors = THEMES[theme]
    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="{CSS.format(theme=theme)}">
<style>
body {{ margin: 0; padding: {outer}px; background: {colors["background"]}; }}
.markdown-body {{ border: 1px solid {colors["border"]}; border-radius: 6px; padding: {inner}px; }}
.d-block {{ display: block !important; }}
.width-fit {{ max-width: 100% !important; }}
</style>
</head>
<body><article class="markdown-body">
{body}
</article></body>
</html>
"""


def page(light_html: str, dark_html: str) -> str:
    bodies = {"light": light_html, "dark": dark_html}
    figures = "\n".join(
        f'<figure><figcaption>{pane["label"]}, {pane["width"]} px</figcaption>'
        f'<iframe width="{pane["width"]}" height="1200" srcdoc="'
        f'{markup.escape(frame(bodies[pane["theme"]], pane["theme"], pane["outer"], pane["inner"]))}"></iframe></figure>'
        for pane in PANES
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Profile README preview</title>
<style>
body {{ margin: 0; padding: 24px; background: #f6f8fa; color: #59636e; font: 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
main {{ display: flex; flex-wrap: wrap; gap: 32px; align-items: flex-start; }}
figure {{ margin: 0; }}
figcaption {{ margin-bottom: 8px; }}
iframe {{ display: block; border: 0; }}
</style>
</head>
<body>
<main>
{figures}
</main>
<script>
for (const pane of document.querySelectorAll("iframe")) {{
  const fit = () => {{ pane.style.height = pane.contentDocument.documentElement.scrollHeight + "px"; }};
  pane.addEventListener("load", () => {{ fit(); new ResizeObserver(fit).observe(pane.contentDocument.body); }});
}}
</script>
</body>
</html>
"""
