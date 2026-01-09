# OER-Forge

Welcome to OER-Forge, a collection of open-source tools built to solve real problems in teaching and learning.

## 📚 About This Repository

This repository contains the source code for the [OER-Forge website](https://oer-forge.github.io/), showcasing tools and resources created for educators and learners. The site is built with [Hugo](https://gohugo.io/) using the [PaperMod](https://github.com/adityatelange/hugo-PaperMod) theme for clean, modern design.

- **Website:** https://oer-forge.github.io/
- **Content:** Tool documentation, announcements, and project information
- **Audience:** Educators, students, and developers interested in open educational resources

## 🧭 Structure

- `content/` — All website content
  - `about.md` — Information about OER-Forge
  - `posts/` — News and announcements
  - `jupyter2hugo/` — Documentation for the Jupyter to Hugo converter
  - `wikiaccess/` — Documentation for the WikiAccess tool
  - `raisemyhand/` — Documentation for the RaiseMyHand classroom tool
- `layouts/` — Custom Hugo templates (if any)
- `static/` — Images, logos, and static assets
- `themes/` — Hugo theme (PaperMod)
- `hugo.toml` — Hugo configuration

## 🛠️ Tools

**[WikiAccess](https://github.com/OER-Forge/wikiaccess)** – Convert DokuWiki pages to accessible, WCAG 2.1 compliant documents. Exports to HTML, Word (.docx), and Markdown.

**[RaiseMyHand](https://github.com/OER-Forge/raisemyhand)** – Real-time classroom question management. Students submit questions anonymously and upvote each other's questions.

**[jupyter2hugo](https://github.com/OER-Forge/jupyter2hugo)** – Convert Jupyter Notebooks into Hugo-compatible Markdown files for seamless integration into Hugo static sites.

## 🚀 Building the Site

This site uses [Hugo](https://gohugo.io/). To build and serve locally:

```sh
hugo server
```

The site will be available at `http://localhost:1313/`.

To build for production:

```sh
hugo
```

This generates the static site in the `public/` directory.

## 📄 License

Content is licensed under the [MIT License](https://opensource.org/licenses/MIT).
