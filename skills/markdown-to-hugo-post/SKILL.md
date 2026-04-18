---
name: markdown-to-hugo-post
description: Create a Hugo blog post in the current site repo from a source markdown file, especially an Obsidian markdown note. Use this when the user wants to import an existing `.md` draft, Obsidian note, or article into `content/posts/` with Hugo front matter, cleaned Obsidian syntax, copied attachments, and site-compatible defaults.
---

# Markdown To Hugo Post

## Overview

This skill converts an existing markdown file into a Hugo post for the current workspace. It is tuned for Obsidian-authored notes: it adds front matter, chooses a slug, rewrites Obsidian image embeds, copies local attachments into `static/posts/<slug>/`, rewrites local markdown image paths when the files exist, normalizes stray empty lines, infers tags and categories, and writes the result into `content/posts/`.

## When To Use

Use this skill when:

- the user gives you a `.md` file and wants it published as a site post
- the user gives you an Obsidian `obsidian://open?...` link and wants that note published
- the source file was written in Obsidian and may contain `![[image.png]]` embeds
- the user has notes or a draft outside `content/posts/` and wants it imported
- the user wants front matter generated automatically from the source content

Do not use this skill when the user wants a post written from scratch without a source markdown file.

## Workflow

1. Inspect the source markdown file.
2. Choose or confirm the output slug.
3. Run `scripts/create_post_from_markdown.py` with the source path and repo root.
4. For Obsidian notes, verify that embedded images were copied into `static/posts/<slug>/` and rewritten to standard Markdown image paths.
5. Review the generated front matter and body, with special attention to `description`, inferred `tags`, inferred `categories`, and whitespace cleanup.
6. Ensure the description is a clean, stand-alone excerpt suitable for listings and social previews. If the generated description feels generic, clipped, or overly long, tighten it before finishing. On overwrite, the script preserves an existing description unless you explicitly pass `--description`.
7. Remove any remaining formatting noise the script did not normalize, especially whitespace-only lines or awkward paragraph gaps.
8. Preview with `make dev` or validate with `hugo --gc --minify`.

## Defaults

The converter script uses these defaults unless the user specifies otherwise:

- output directory: `content/posts/`
- title: first H1 in the source file, otherwise the source filename
- slug: slugified title, otherwise slugified source filename
- date: current local time
- draft: `false`
- description: a short editorial summary that stands on its own without repeating the title; prefer a clean sentence-level excerpt and avoid clipped `...` endings
- tags: inferred from the title/body when not explicitly provided
- categories: inferred from the title/body when not explicitly provided
- `toc`: `true` if the body contains `## ` headings, otherwise `false`
- `readingTime`: `true`
- `featured`: `false`
- embedded Obsidian images: copied from the source file directory into `static/posts/<slug>/` and rewritten as `/posts/<slug>/<filename>`
- existing description on overwrite: preserved unless `--description` is explicitly provided
- body spacing: trims whitespace-only lines and collapses repeated blank gaps to single empty lines

If the source file starts with a top-level `# Heading`, the script uses that as the title and removes it from the body to avoid duplicate titles on the post page.

If the source contains `![[filename.ext]]`, the script looks for that file relative to the source markdown file, copies it into the Hugo site's `static/posts/<slug>/` directory, and rewrites the embed as a standard Markdown image.

If the source contains a standard Markdown image like `![alt](images/foo.png)` and the file exists relative to the source markdown file, the script copies that asset and rewrites the path too.

## Commands

Basic usage:

```bash
python3 /Users/haifengxu/.codex/skills/markdown-to-hugo-post/scripts/create_post_from_markdown.py \
  "/path/to/Obsidian Note.md" \
  --repo /path/to/site-repo
```

Obsidian URI usage:

```bash
python3 /Users/haifengxu/.codex/skills/markdown-to-hugo-post/scripts/create_post_from_markdown.py \
  "obsidian://open?vault=markdowns&file=My%20Note" \
  --repo /path/to/site-repo
```

Override common fields:

```bash
python3 /Users/haifengxu/.codex/skills/markdown-to-hugo-post/scripts/create_post_from_markdown.py \
  /path/to/source.md \
  --repo /path/to/site-repo \
  --slug hello-world \
  --title "Hello world!" \
  --date 2024-04-18T09:00:00-07:00 \
  --tags notes,intro \
  --categories Essays,Notes \
  --draft false
```

## Output Contract

The generated file should:

- land in `content/posts/<slug>.md`
- use TOML front matter compatible with this site
- preserve the source markdown body with minimal transformation
- normalize whitespace-only blank lines into standard Markdown paragraph spacing
- convert Obsidian `![[...]]` image embeds into standard Markdown images
- copy embedded image files into `static/posts/<slug>/`
- rewrite local Markdown image paths when the source asset exists
- generate sensible tags and categories when they are not explicitly provided
- avoid overwriting an existing post unless `--force` is provided

## Resources

### scripts/create_post_from_markdown.py

Deterministically converts a markdown file into a Hugo post with site-compatible front matter.

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

**Not every skill requires all three types of resources.**
