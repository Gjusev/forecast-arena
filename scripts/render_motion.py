"""Render the motion piece and brand assets from assets/video/src/index.html.

Deterministic: each frame is renderAt(t) screenshotted by system Chrome, piped to
ffmpeg. Needs Chrome + ffmpeg on PATH.

    uv run python scripts/export_story_data.py
    uv run --with playwright python scripts/render_motion.py [all|video|stills|brand]
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets/video/src/index.html"
VIDEO = ROOT / "assets/video"
BRAND = ROOT / "assets/brand"
FPS = 30
STILLS = {  # name -> second; the resting frame at the end of each scene
    "01-trains-miss": 10.0,
    "02-trains-board": 14.4,
    "03-power-catch": 20.6,
    "04-power-board": 24.8,
    "05-money": 29.2,
}


def open_page(p):
    browser = p.chromium.launch(channel="chrome")
    page = browser.new_page(viewport={"width": 1920, "height": 1080})
    page.goto(SRC.as_uri())
    page.evaluate("document.fonts.ready")
    story = json.loads((VIDEO / "story.json").read_text(encoding="utf-8"))
    duration = page.evaluate("s => setup(s)", story)
    return browser, page, duration


def shot(page, t: float) -> bytes:
    page.evaluate("t => renderAt(t)", t)
    return page.screenshot(type="png")


def video(page, duration: float) -> None:
    mp4 = VIDEO / "forecast-arena.mp4"
    ff = subprocess.Popen(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-f",
            "image2pipe",
            "-framerate",
            str(FPS),
            "-i",
            "-",
            "-c:v",
            "libx264",
            "-preset",
            "slow",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(mp4),
        ],
        stdin=subprocess.PIPE,
    )
    n = round(duration * FPS)
    for i in range(n + 1):
        ff.stdin.write(shot(page, i / FPS))
        if i % 150 == 0:
            print(f"  frame {i}/{n}")
    ff.stdin.close()
    if ff.wait():
        sys.exit("ffmpeg failed")
    gif = VIDEO / "preview.gif"
    subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-loglevel",
            "error",
            "-i",
            str(mp4),
            "-vf",
            "fps=12,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=48:stats_mode=diff[p];"
            "[b][p]paletteuse=dither=none:diff_mode=rectangle",
            str(gif),
        ],
        check=True,
    )
    print("->", mp4, mp4.stat().st_size // 1024, "KB |", gif, gif.stat().st_size // 1024, "KB")


def stills(page) -> None:
    out = VIDEO / "stills"
    out.mkdir(exist_ok=True)
    for name, t in STILLS.items():
        (out / f"{name}.png").write_bytes(shot(page, t))
    print("->", out)


def brand(page) -> None:
    BRAND.mkdir(parents=True, exist_ok=True)
    # banner / social preview: the resting title frame cropped to 2:1
    page.evaluate("renderAt(3.25)")
    page.screenshot(
        path=str(BRAND / "banner.png"), clip={"x": 0, "y": 44, "width": 1920, "height": 960}
    )
    page.evaluate("renderMark(512)")
    page.set_viewport_size({"width": 512, "height": 512})
    page.screenshot(
        path=str(BRAND / "mark-512.png"), clip={"x": 0, "y": 0, "width": 512, "height": 512}
    )
    svg = page.evaluate("document.getElementById('stage').outerHTML")
    svg = svg.replace('width="512" height="512"', 'width="64" height="64"').replace(
        ' id="stage"', ""
    )
    (BRAND / "mark.svg").write_text(svg + "\n", encoding="utf-8")
    page.set_viewport_size({"width": 1920, "height": 1080})
    print("->", BRAND)


def main() -> None:
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    with sync_playwright() as p:
        browser, page, duration = open_page(p)
        if what in ("all", "stills"):
            stills(page)
        if what in ("all", "brand"):
            brand(page)
        if what in ("all", "video"):
            video(page, duration)
        browser.close()


if __name__ == "__main__":
    main()
