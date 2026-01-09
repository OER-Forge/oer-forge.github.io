---
title: jupyter2hugo
description: A command-line tool to convert Jupyter Notebooks into Hugo-compatible Markdown files
draft: false
---

![jupyter2hugo Screenshot](/jupyter2hugo.png)

jupyter2hugo converts Jupyter Book projects to Hugo static sites with proper navigation, internal links, and WCAG 2.1 compliance.

## Features

- **Complete conversion** from Jupyter Book (`_toc.yml`) to Hugo static sites
- **Theme-agnostic output** - works with any Hugo theme
- **Navigation preservation** - parts, chapters, and sections from TOC
- **Internal link rewriting** - converts relative paths to Hugo URLs
- **Math support** - KaTeX rendering for LaTeX equations
- **YouTube embeds** - converts to Hugo shortcodes
- **Image handling** - preserves directory structure
- **Code cells** - preserves outputs and syntax highlighting
- **MyST directives** - converts to Hugo shortcodes (admonitions, notes, warnings)
- **Accessibility** - optional WCAG 2.1 compliance checking


## Requirements

- Python 3.8+
- Hugo (for building the site)
- Node.js and npm (optional, for accessibility checking)

---

## License

[MIT License](https://opensource.org/licenses/MIT)