#!/usr/bin/env python3
"""
Migrate a brond post's inline base64 <img> tags to separate image files.

Only the oldest postings (published before the "separate image file" convention
started) still embed images as base64 data URIs directly in the post HTML,
bloating the file to several MB and making them incompatible with the
Naver-copy workflow (which needs a real https:// URL per image). This script
turns such a post into the modern format: real files under
posts/images/<slug>/, referenced by relative path.

Two-step usage so a human/Claude can pick sensible filenames before anything
is written:

  1) List mode -- inspect what's embedded, write nothing:
       python3 migrate_base64_images.py list posts/<slug>.html

     Prints, for each embedded image in document order: index, inferred
     extension, and its alt text. Use the alt text to decide a short
     descriptive filename for each one (e.g. "cover.jpg", "unit-84a.png").

  2) Apply mode -- decode, save, rewrite, and verify:
       python3 migrate_base64_images.py apply posts/<slug>.html <slug> \
           --names cover.jpg,location-map.png,unit-84a.png,...

     --names must list exactly as many comma-separated filenames as there are
     embedded images, in the same document order list mode printed them in.
     This:
       - decodes each base64 image and writes it to posts/images/<slug>/<name>
       - rewrites each matching <img src="data:...;base64,...."> in the HTML
         to <img src="images/<slug>/<name>">, in order
       - re-reads the result and diffs it against the original (with both
         sides' image src values blanked out) to confirm nothing else in the
         HTML changed -- this is the safety check that makes it OK to trust
         an automated rewrite of a live production file
       - refuses to write anything if the counts don't match or the diff
         check fails

  The script never runs git commands itself -- committing/pushing the result
  is a separate, explicit step (see SKILL.md) because it touches the live site.
"""
import argparse
import base64
import re
import sys
from pathlib import Path

IMG_PATTERN = re.compile(
    r'<img src="data:image/(?P<ext>[a-zA-Z0-9.+-]+);base64,(?P<data>[^"]+)"'
    r'(?P<mid>[^>]*?)alt="(?P<alt>[^"]*)"'
)


def normalize_ext(ext: str) -> str:
    return "jpg" if ext.lower() == "jpeg" else ext.lower()


def cmd_list(html_path: Path) -> None:
    content = html_path.read_text(encoding="utf-8")
    matches = list(IMG_PATTERN.finditer(content))
    if not matches:
        print(f"No base64 <img> tags found in {html_path}. "
              f"This post may already be in the modern (separate-file) format.")
        return
    print(f"Found {len(matches)} embedded image(s) in {html_path}, in document order:\n")
    for i, m in enumerate(matches, 1):
        ext = normalize_ext(m.group("ext"))
        size_kb = len(base64.b64decode(m.group("data"))) // 1024
        print(f"  {i:2d}. .{ext:<4} ~{size_kb:>5}KB  alt=\"{m.group('alt')}\"")
    print(
        "\nPick a short descriptive filename for each (based on the alt text), "
        "then run:\n"
        f"  python3 {Path(__file__).name} apply {html_path} <slug> --names "
        "name1.ext,name2.ext,..."
    )


def cmd_apply(html_path: Path, slug: str, names: list[str]) -> None:
    original = html_path.read_text(encoding="utf-8")
    matches = list(IMG_PATTERN.finditer(original))
    if not matches:
        sys.exit(f"No base64 <img> tags found in {html_path} -- nothing to migrate.")
    if len(names) != len(matches):
        sys.exit(
            f"--names has {len(names)} entries but {len(matches)} embedded images "
            f"were found. Run list mode again and match the count exactly."
        )

    img_dir = html_path.parent / "images" / slug

    # First pass: decode into memory and build the rewritten HTML, but don't
    # touch disk yet -- the safety check below needs to pass first.
    decoded: list[tuple[str, bytes]] = []

    def repl(m: re.Match) -> str:
        idx = len(decoded)
        fname = names[idx]
        decoded.append((fname, base64.b64decode(m.group("data"))))
        rel_src = f"images/{slug}/{fname}"
        return f'<img src="{rel_src}"{m.group("mid")}alt="{m.group("alt")}"'

    rewritten = IMG_PATTERN.sub(repl, original)

    # Safety check: blank out only the <img> tags this migration touches on
    # both sides (the base64 ones in the original, the new relative-path ones
    # in the rewrite) and require the two documents to then be byte-identical.
    # Any other difference -- a stray attribute reordered, whitespace changed,
    # anything -- means something unexpected happened and this rewrite should
    # not be trusted on a live production file.
    original_blanked = re.sub(
        r'<img src="data:image/[a-zA-Z0-9.+-]+;base64,[^"]+"',
        '<img src="[IMG]"',
        original,
    )
    rewritten_blanked = re.sub(
        r'<img src="images/' + re.escape(slug) + r'/[^"]+"',
        '<img src="[IMG]"',
        rewritten,
    )
    if original_blanked != rewritten_blanked:
        sys.exit(
            "SAFETY CHECK FAILED: the rewritten HTML differs from the original "
            "by more than just the image src attributes. Nothing was written "
            "to disk. Investigate the diff manually before trusting this "
            "migration (e.g. diff the two _blanked strings this script computes)."
        )

    # Safety check passed -- now it's safe to actually write files.
    img_dir.mkdir(parents=True, exist_ok=True)
    for fname, raw in decoded:
        (img_dir / fname).write_bytes(raw)
    html_path.write_text(rewritten, encoding="utf-8")
    print(f"OK: {html_path} rewritten ({len(original):,} -> {len(rewritten):,} bytes).")
    print(f"OK: {len(names)} image file(s) written under {img_dir}/")
    print(
        "Safety check passed: rewritten HTML is byte-identical to the original "
        "except for the <img> src attributes.\n"
    )
    print(
        "Next: this is a live-site change. Do not commit/push it yourself -- "
        "show the user `git status` / `git diff --stat` and a proposed commit "
        "message, get their go-ahead, then follow the repo's normal commit+push "
        "flow (see SKILL.md's git safety notes)."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="mode", required=True)

    p_list = sub.add_parser("list", help="Show embedded images without writing anything")
    p_list.add_argument("html_path", type=Path)

    p_apply = sub.add_parser("apply", help="Decode, save, rewrite, and verify")
    p_apply.add_argument("html_path", type=Path)
    p_apply.add_argument("slug", help="Post slug, e.g. geomam-prugio-pravenue")
    p_apply.add_argument("--names", required=True, help="Comma-separated filenames, in document order")

    args = parser.parse_args()
    if args.mode == "list":
        cmd_list(args.html_path)
    else:
        names = [n.strip() for n in args.names.split(",")]
        cmd_apply(args.html_path, args.slug, names)


if __name__ == "__main__":
    main()
