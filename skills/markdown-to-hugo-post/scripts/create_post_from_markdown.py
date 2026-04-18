#!/usr/bin/env python3

from __future__ import annotations

import argparse
import shutil
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-") or "post"


def parse_bool(raw: str) -> bool:
    lowered = raw.strip().lower()
    if lowered in {"true", "1", "yes", "y"}:
        return True
    if lowered in {"false", "0", "no", "n"}:
        return False
    raise argparse.ArgumentTypeError(f"invalid boolean value: {raw}")


def infer_title_and_body(text: str, fallback_title: str) -> tuple[str, str]:
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        title = lines[0][2:].strip() or fallback_title
        body = "\n".join(lines[1:]).lstrip("\n")
        return title, body
    return fallback_title, text.lstrip()


def normalize_body_spacing(text: str) -> str:
    lines = [line.rstrip() for line in text.splitlines()]
    normalized: list[str] = []
    blank_pending = False

    for line in lines:
        if not line.strip():
            blank_pending = True
            continue
        if blank_pending and normalized:
            normalized.append("")
        normalized.append(line)
        blank_pending = False

    cleaned = "\n".join(normalized).strip()
    # Keep compact Markdown lists even if the source had spacer lines between bullets.
    cleaned = re.sub(r"(?m)(^[-*] .+)\n\n(?=[-*] )", r"\1\n", cleaned)
    cleaned = re.sub(r"(?m)(^\d+\. .+)\n\n(?=\d+\. )", r"\1\n", cleaned)
    return cleaned


def sentence_case(value: str) -> str:
    if not value:
        return value
    return value[0].lower() + value[1:]


def clean_heading(value: str) -> str:
    value = re.sub(r"`([^`]+)`", r"\1", value)
    value = re.sub(r"\*([^*]+)\*", r"\1", value)
    value = value.replace('"', "")
    return re.sub(r"\s+", " ", value).strip(" .:-")


def strip_markdown(value: str) -> str:
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = value.replace("**", "").replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", value).strip()


def split_sentences(value: str) -> list[str]:
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", value) if part.strip()]


def truncate_at_word_boundary(value: str, limit: int) -> str:
    if len(value) <= limit:
        return value
    truncated = value[: limit + 1].rsplit(" ", 1)[0].strip()
    if not truncated:
        truncated = value[:limit].strip()
    return truncated.rstrip(" ,;:-")


def infer_description(title: str, body: str) -> str:
    headings: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            heading = clean_heading(line[3:].strip())
            if heading:
                headings.append(heading)

    if title and headings:
        heading = sentence_case(headings[0])
        if re.match(r"^(why|how|when|what)\b", heading):
            description = heading[0].upper() + heading[1:] + "."
        else:
            description = f"When {heading}."
        if len(description) <= 160:
            return description

    for block in re.split(r"\n\s*\n", body):
        stripped = block.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            continue
        if stripped.startswith("!["):
            continue
        single_line = strip_markdown(stripped)
        if not single_line:
            continue

        sentences = split_sentences(single_line)
        if sentences:
            candidate = ""
            for sentence in sentences:
                proposal = f"{candidate} {sentence}".strip() if candidate else sentence
                if len(proposal) > 160:
                    break
                candidate = proposal
                if len(candidate) >= 110:
                    return candidate
            if candidate:
                return candidate

        return truncate_at_word_boundary(single_line, 160)
    return ""


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def infer_tags_and_categories(title: str, body: str) -> tuple[list[str], list[str]]:
    haystack = f"{title}\n{body}".lower()

    rule_set = [
        {
            "match": ["ai", "artificial intelligence", "agent", "agents", "chatgpt", "llm", "llms"],
            "tags": ["ai"],
            "categories": ["AI"],
        },
        {
            "match": ["engineer", "engineering", "code", "coding", "software"],
            "tags": ["engineering"],
            "categories": ["Technology"],
        },
        {
            "match": ["judgment", "discernment", "metacognition", "cognitive stewardship"],
            "tags": ["judgment"],
            "categories": ["Thinking"],
        },
        {
            "match": ["knowledge work", "manager", "writer", "analyst", "consultant", "professional identity"],
            "tags": ["knowledge work"],
            "categories": ["Work"],
        },
        {
            "match": ["productivity", "flow", "mindfulness"],
            "tags": ["productivity"],
            "categories": ["Work"],
        },
        {
            "match": ["reflection", "meaning", "value", "identity"],
            "tags": ["reflection"],
            "categories": ["Essays"],
        },
    ]

    tags: list[str] = []
    categories: list[str] = []
    for rule in rule_set:
        if any(token in haystack for token in rule["match"]):
            tags.extend(rule["tags"])
            categories.extend(rule["categories"])

    return unique_preserving_order(tags)[:5], unique_preserving_order(categories)[:3]


def toml_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def asset_name(filename: str) -> str:
    path = Path(filename)
    stem = slugify(path.stem)
    suffix = path.suffix.lower()
    return f"{stem}{suffix}"


def resolve_obsidian_source(raw_source: str) -> Path:
    parsed = urlparse(raw_source)
    if parsed.scheme != "obsidian":
        return Path(raw_source).expanduser().resolve()

    if parsed.netloc != "open":
        raise ValueError(f"Unsupported Obsidian URI action: {parsed.netloc or parsed.path}")

    query = parse_qs(parsed.query)
    vault = unquote(query.get("vault", [""])[0]).strip()
    file_name = unquote(query.get("file", [""])[0]).strip()
    if not vault or not file_name:
        raise ValueError("Obsidian URI must include both vault and file query parameters")

    relative_file = Path(file_name)
    candidate_relatives = [relative_file]
    if not relative_file.suffix:
        candidate_relatives.append(relative_file.with_suffix(".md"))

    vault_roots = [
        Path.home() / "Library" / "Mobile Documents" / "iCloud~md~obsidian" / "Documents" / vault,
        Path.home() / "Documents" / vault,
        Path.home() / "Obsidian" / vault,
    ]

    for vault_root in vault_roots:
        for candidate_relative in candidate_relatives:
            candidate = (vault_root / candidate_relative).expanduser()
            if candidate.is_file():
                return candidate.resolve()

    searched = ", ".join(str(root) for root in vault_roots)
    raise ValueError(
        f"Could not resolve Obsidian file '{file_name}' in vault '{vault}'. Searched: {searched}"
    )


def rewrite_obsidian_embeds(body: str, source_dir: Path, static_dir: Path, slug: str) -> str:
    target_dir = static_dir / "posts" / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    def replace(match: re.Match[str]) -> str:
        original = match.group(1).strip()
        source_asset = source_dir / original
        if not source_asset.is_file():
            return f"*Missing embedded asset: {original}*"
        copied_name = asset_name(original)
        shutil.copy2(source_asset, target_dir / copied_name)
        alt = Path(original).stem.replace("-", " ").replace("_", " ").strip()
        return f"![{alt}](/posts/{slug}/{copied_name})"

    return re.sub(r"!\[\[([^\]]+)\]\]", replace, body)


def rewrite_markdown_images(body: str, source_dir: Path, static_dir: Path, slug: str) -> str:
    target_dir = static_dir / "posts" / slug
    target_dir.mkdir(parents=True, exist_ok=True)

    def replace(match: re.Match[str]) -> str:
        alt = match.group(1)
        raw_path = match.group(2).strip()
        if raw_path.startswith(("http://", "https://", "/")):
            return match.group(0)
        source_asset = (source_dir / raw_path).resolve()
        try:
            source_asset.relative_to(source_dir.resolve())
        except ValueError:
            return match.group(0)
        if not source_asset.is_file():
            return match.group(0)
        copied_name = asset_name(source_asset.name)
        shutil.copy2(source_asset, target_dir / copied_name)
        return f"![{alt}](/posts/{slug}/{copied_name})"

    return re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", replace, body)


def read_existing_front_matter_value(path: Path, key: str) -> str | None:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    if not text.startswith("+++\n"):
        return None
    parts = text.split("+++\n", 2)
    if len(parts) < 3:
        return None
    front_matter = parts[1]
    match = re.search(rf'^{re.escape(key)}\s*=\s*"((?:[^"\\]|\\.)*)"$', front_matter, re.MULTILINE)
    if not match:
        return None
    value = match.group(1)
    return value.replace('\\"', '"').replace("\\\\", "\\")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert a markdown file into a Hugo post in content/posts/."
    )
    parser.add_argument("source", help="Path to the source markdown file")
    parser.add_argument("--repo", required=True, help="Path to the Hugo site repo root")
    parser.add_argument("--slug", help="Output slug")
    parser.add_argument("--title", help="Post title")
    parser.add_argument("--date", help="ISO 8601 date for front matter")
    parser.add_argument("--description", help="Post description")
    parser.add_argument("--tags", help="Comma-separated tag list")
    parser.add_argument("--categories", help="Comma-separated category list")
    parser.add_argument("--draft", type=parse_bool, default=False, help="Draft status")
    parser.add_argument("--featured", type=parse_bool, default=False, help="Featured status")
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing output file if present"
    )
    args = parser.parse_args()

    try:
        source_path = resolve_obsidian_source(args.source)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    repo_path = Path(args.repo).expanduser().resolve()
    if not source_path.is_file():
        print(f"Source file not found: {source_path}", file=sys.stderr)
        return 1
    posts_dir = repo_path / "content" / "posts"
    static_dir = repo_path / "static"
    if not posts_dir.is_dir():
        print(f"Posts directory not found: {posts_dir}", file=sys.stderr)
        return 1
    if not static_dir.is_dir():
        print(f"Static directory not found: {static_dir}", file=sys.stderr)
        return 1

    raw_text = source_path.read_text(encoding="utf-8")
    fallback_title = args.title or source_path.stem.replace("-", " ").replace("_", " ").strip()
    inferred_title, body = infer_title_and_body(raw_text, fallback_title)
    title = args.title or inferred_title
    slug = args.slug or slugify(title or source_path.stem)
    body = rewrite_obsidian_embeds(body, source_path.parent, static_dir, slug)
    body = rewrite_markdown_images(body, source_path.parent, static_dir, slug)
    body = normalize_body_spacing(body)
    date = args.date or datetime.now().astimezone().isoformat(timespec="seconds")
    output_path = posts_dir / f"{slug}.md"
    if output_path.exists() and not args.force:
        print(f"Refusing to overwrite existing file: {output_path}", file=sys.stderr)
        return 1

    existing_description = None
    if output_path.exists() and args.force and args.description is None:
        existing_description = read_existing_front_matter_value(output_path, "description")

    description = args.description or existing_description or infer_description(title, body)
    inferred_tags, inferred_categories = infer_tags_and_categories(title, body)
    tags = [tag.strip() for tag in (args.tags or "").split(",") if tag.strip()] or inferred_tags
    categories = [
        category.strip() for category in (args.categories or "").split(",") if category.strip()
    ] or inferred_categories
    toc = "## " in body

    tags_literal = ", ".join(f'"{toml_escape(tag)}"' for tag in tags)
    categories_literal = ", ".join(f'"{toml_escape(category)}"' for category in categories)

    front_matter = [
        "+++",
        f'title = "{toml_escape(title)}"',
        f"date = {date}",
        f"draft = {'true' if args.draft else 'false'}",
        f'description = "{toml_escape(description)}"',
        f"tags = [{tags_literal}]",
        f"categories = [{categories_literal}]",
        f"toc = {'true' if toc else 'false'}",
        "readingTime = true",
        f"featured = {'true' if args.featured else 'false'}",
        "+++",
        "",
    ]
    content = "\n".join(front_matter) + body.rstrip() + "\n"
    output_path.write_text(content, encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
