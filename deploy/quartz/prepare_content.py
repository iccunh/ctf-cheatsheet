from __future__ import annotations

import argparse
import json
import pathlib
import posixpath
import re
import shutil
import urllib.parse

EXCLUDED_DIRS = {
    ".git",
    ".gitbook",
    ".github",
    ".quartz",
    "content",
    "deploy",
    "node_modules",
    "public",
}

FENCE_RE = re.compile(r"(^```[\s\S]*?^```|^~~~[\s\S]*?^~~~)", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"\A---\r?\n([\s\S]*?)\r?\n---\r?\n?")
SUMMARY_ITEM_RE = re.compile(r"^(\s*)\*\s+\[([^\]]+)\]\(([^)]+)\)\s*$", re.MULTILINE)
EMBED_RE = re.compile(r"\{%\s*embed\s+url=\"([^\"]+)\"\s*%\}")
FIGURE_IMG_RE = re.compile(
    r"<figure>\s*<img\s+src=\"([^\"]+)\"(?:\s+alt=\"([^\"]*)\")?[^>]*>\s*(?:<figcaption>(.*?)</figcaption>)?\s*</figure>",
    re.IGNORECASE | re.DOTALL,
)
MD_LINK_RE = re.compile(r"(!?\[[^\]]*\])\(([^)]+)\)")
H1_RE = re.compile(r"^\s*#\s+(.+?)\s*$", re.MULTILINE)


def sanitize_asset_name(name: str) -> str:
    stem, ext = posixpath.splitext(name)
    clean_stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-")
    clean_stem = re.sub(r"-{2,}", "-", clean_stem)
    return f"{clean_stem or 'asset'}{ext.lower()}"


def sanitize_md_rel_path(rel_posix: str) -> str:
    parts = rel_posix.split("/")
    if parts[-1].lower() == "readme.md":
        parts[-1] = "index.md"
    else:
        stem, ext = posixpath.splitext(parts[-1])
        # Replace '+' in filenames so URLs and slugs stay unambiguous
        stem = stem.replace("-+-", "-").replace("+", "-plus-")
        stem = re.sub(r"[^a-zA-Z0-9._-]+", "-", stem).strip("-")
        stem = re.sub(r"-{2,}", "-", stem)
        parts[-1] = f"{stem}{ext}"
    return "/".join(parts)


def dest_path_to_slug(dest_rel_posix: str) -> str:
    without_ext = re.sub(r"\.md$", "", dest_rel_posix, flags=re.IGNORECASE)
    return without_ext


def parse_summary(summary_text: str) -> tuple[dict[str, str], list[tuple[int, str, str]]]:
    title_map: dict[str, str] = {}
    entries: list[tuple[int, str, str]] = []
    for match in SUMMARY_ITEM_RE.finditer(summary_text):
        indent_str, title, raw_path = match.groups()
        rel_path = raw_path.strip().lstrip("./")
        depth = len(indent_str.replace("\t", "  ")) // 2
        title_map[rel_path] = title.strip()
        entries.append((depth, title.strip(), rel_path))
    return title_map, entries


def build_path_map(repo_root: pathlib.Path) -> dict[str, str]:
    path_map: dict[str, str] = {}
    for md_file in sorted(repo_root.rglob("*.md")):
        rel_parts = md_file.relative_to(repo_root).parts
        if any(part in EXCLUDED_DIRS for part in rel_parts):
            continue
        if rel_parts == ("SUMMARY.md",):
            continue
        src_rel = "/".join(rel_parts)
        path_map[src_rel] = sanitize_md_rel_path(src_rel)
    return path_map


def build_order_map(
    entries: list[tuple[int, str, str]], path_map: dict[str, str]
) -> dict[str, int]:
    order_map: dict[str, int] = {}
    for idx, (_, _, src_rel) in enumerate(entries):
        dest_rel = path_map.get(src_rel, sanitize_md_rel_path(src_rel))
        slug = dest_path_to_slug(dest_rel)
        order_map[slug] = idx
        if slug.endswith("/index"):
            folder_slug = slug[: -len("/index")]
            order_map.setdefault(folder_slug, idx)
    return order_map


def extract_frontmatter(raw_text: str) -> tuple[dict[str, str], str]:
    meta: dict[str, str] = {}
    match = FRONTMATTER_RE.match(raw_text)
    if not match:
        return meta, raw_text
    fm_block = match.group(1)
    body = raw_text[match.end() :]
    for line in fm_block.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key and val:
                meta[key] = val
    return meta, body


def format_frontmatter(meta: dict[str, str]) -> str:
    lines = ["---"]
    for key, val in meta.items():
        escaped = val.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f'{key}: "{escaped}"')
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def rewrite_non_code_segment(
    segment: str,
    src_rel: str,
    path_map: dict[str, str],
    asset_map: dict[str, str],
) -> str:
    src_dir = posixpath.dirname(src_rel)

    def replace_embed(match: re.Match[str]) -> str:
        url = match.group(1).strip()
        return f"- [{url}]({url})"

    def replace_figure(match: re.Match[str]) -> str:
        raw_src, alt, caption = match.groups()
        decoded_src = urllib.parse.unquote(raw_src.strip())
        base_name = posixpath.basename(decoded_src)
        mapped_asset = asset_map.get(base_name, sanitize_asset_name(base_name))
        alt_text = (alt or caption or "").strip()
        return f"![{alt_text}](assets/{mapped_asset})"

    def replace_md_link(match: re.Match[str]) -> str:
        label_part, raw_target = match.groups()
        target = raw_target.strip()
        if (
            not target
            or target.startswith("#")
            or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target)
        ):
            return match.group(0)

        if "#" in target:
            path_part, anchor_part = target.split("#", 1)
            anchor_suffix = f"#{anchor_part}"
        else:
            path_part, anchor_suffix = target, ""

        decoded_path = urllib.parse.unquote(path_part.strip())
        if not decoded_path:
            return match.group(0)

        # Check if it points to .gitbook/assets
        if ".gitbook/assets/" in decoded_path:
            base_name = posixpath.basename(decoded_path)
            mapped_asset = asset_map.get(base_name, sanitize_asset_name(base_name))
            return f"{label_part}(assets/{mapped_asset}{anchor_suffix})"

        if decoded_path.startswith("assets/"):
            return match.group(0)

        norm_src = posixpath.normpath(posixpath.join(src_dir, decoded_path)).lstrip("./")
        if norm_src in path_map:
            return f"{label_part}({path_map[norm_src]}{anchor_suffix})"
        if f"{norm_src}.md" in path_map:
            return f"{label_part}({path_map[f'{norm_src}.md']}{anchor_suffix})"
        if f"{norm_src}/README.md" in path_map:
            return f"{label_part}({path_map[f'{norm_src}/README.md']}{anchor_suffix})"

        return match.group(0)

    out = EMBED_RE.sub(replace_embed, segment)
    out = FIGURE_IMG_RE.sub(replace_figure, out)
    out = MD_LINK_RE.sub(replace_md_link, out)
    return out


def render_summary_toc(
    entries: list[tuple[int, str, str]], path_map: dict[str, str]
) -> str:
    lines = ["## Directory", ""]
    for depth, title, src_rel in entries:
        if src_rel == "README.md":
            continue
        dest_rel = path_map.get(src_rel, sanitize_md_rel_path(src_rel))
        indent = "  " * max(0, depth)
        lines.append(f"{indent}- [{title}]({dest_rel})")
    return "\n".join(lines) + "\n"


def render_folder_children(
    src_rel: str,
    entries: list[tuple[int, str, str]],
    path_map: dict[str, str],
) -> str:
    # Find this folder's entry in SUMMARY.md and list its direct/nested children
    target_idx = None
    target_depth = 0
    for idx, (depth, _, entry_src) in enumerate(entries):
        if entry_src == src_rel:
            target_idx = idx
            target_depth = depth
            break
    if target_idx is None:
        return ""

    child_lines: list[str] = []
    for depth, title, child_src in entries[target_idx + 1 :]:
        if depth <= target_depth:
            break
        dest_rel = path_map.get(child_src, sanitize_md_rel_path(child_src))
        rel_indent = "  " * (depth - target_depth - 1)
        child_lines.append(f"{rel_indent}- [{title}]({dest_rel})")

    if not child_lines:
        return ""
    return "\n## Topics\n\n" + "\n".join(child_lines) + "\n"


def transform_markdown(
    raw_text: str,
    src_rel: str,
    title_map: dict[str, str],
    entries: list[tuple[int, str, str]],
    path_map: dict[str, str],
    asset_map: dict[str, str],
) -> str:
    meta, body = extract_frontmatter(raw_text)
    parts = FENCE_RE.split(body)

    # Extract fallback H1 from first non-code segment if present, and strip duplicate top H1
    first_h1: str | None = None
    for i in range(0, len(parts), 2):
        h1_match = H1_RE.search(parts[i])
        if h1_match:
            first_h1 = h1_match.group(1).strip()
            # Remove only the first top-level H1 heading so Quartz ArticleTitle doesn't duplicate it
            parts[i] = H1_RE.sub("", parts[i], count=1).lstrip("\r\n")
            break

    title = title_map.get(src_rel) or meta.get("title") or first_h1
    if not title:
        stem = posixpath.splitext(posixpath.basename(src_rel))[0]
        title = stem.replace("-", " ").title()
    meta["title"] = title

    for i in range(0, len(parts), 2):
        parts[i] = rewrite_non_code_segment(parts[i], src_rel, path_map, asset_map)

    transformed_body = "".join(parts).strip()

    if src_rel == "README.md":
        toc_block = render_summary_toc(entries, path_map)
        transformed_body = f"{transformed_body}\n\n{toc_block}".strip()
    elif src_rel.endswith("/README.md") and "](" not in transformed_body:
        children_block = render_folder_children(src_rel, entries, path_map)
        if children_block:
            transformed_body = f"{transformed_body}\n{children_block}".strip()

    return format_frontmatter(meta) + transformed_body + "\n"


def prepare_content(
    repo_root: pathlib.Path,
    output_dir: pathlib.Path,
    layout_file: pathlib.Path | None = None,
) -> dict[str, int]:
    summary_path = repo_root / "SUMMARY.md"
    summary_text = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
    title_map, entries = parse_summary(summary_text)
    path_map = build_path_map(repo_root)
    order_map = build_order_map(entries, path_map)

    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    asset_map: dict[str, str] = {}
    gitbook_assets_dir = repo_root / ".gitbook" / "assets"
    if gitbook_assets_dir.is_dir():
        dest_assets_dir = output_dir / "assets"
        dest_assets_dir.mkdir(parents=True, exist_ok=True)
        for asset_file in sorted(gitbook_assets_dir.iterdir()):
            if asset_file.is_file():
                clean_name = sanitize_asset_name(asset_file.name)
                asset_map[asset_file.name] = clean_name
                shutil.copy2(asset_file, dest_assets_dir / clean_name)

    for src_rel, dest_rel in path_map.items():
        src_path = repo_root / pathlib.Path(src_rel)
        dest_path = output_dir / pathlib.Path(dest_rel)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        raw_text = src_path.read_text(encoding="utf-8")
        out_text = transform_markdown(
            raw_text=raw_text,
            src_rel=src_rel,
            title_map=title_map,
            entries=entries,
            path_map=path_map,
            asset_map=asset_map,
        )
        dest_path.write_text(out_text, encoding="utf-8", newline="\n")

    if layout_file and layout_file.exists():
        layout_text = layout_file.read_text(encoding="utf-8")
        order_json = json.dumps(order_map, sort_keys=True)
        updated_layout = layout_text.replace("/* __SUMMARY_ORDER__ */ {}", order_json)
        layout_file.write_text(updated_layout, encoding="utf-8", newline="\n")

    return {
        "markdown_files": len(path_map),
        "assets": len(asset_map),
        "ordered_slugs": len(order_map),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=pathlib.Path,
        default=pathlib.Path(__file__).resolve().parents[2],
        help="Path to the ctf-cheatsheet repository root",
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        required=True,
        help="Path to the Quartz content directory to populate",
    )
    parser.add_argument(
        "--layout-file",
        type=pathlib.Path,
        default=None,
        help="Optional path to quartz.layout.ts to inject SUMMARY.md order map",
    )
    args = parser.parse_args()
    stats = prepare_content(
        repo_root=args.repo_root.resolve(),
        output_dir=args.output_dir.resolve(),
        layout_file=args.layout_file.resolve() if args.layout_file else None,
    )
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
