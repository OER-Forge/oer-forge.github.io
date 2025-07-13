# BUILD-NOTES.md

## Webpage Styling and Template Plan

### 1. Template Structure
- **Split templates into:**
  - `header.html`: Contains site header and navigation menu.
  - `footer.html`: Contains site footer and copyright/license info.
  - `page.html`: Main content template, includes header and footer via placeholders.
- **Benefits:**
  - Easier maintenance and professional structure.
  - Reusable header/footer across all pages.

### 2. Navigation Menu
- **Top-level only:**
  - Only items with `menu: true` in `toc:` are included.
  - No submenus for now.
- **Accessibility:**
  - Use `<nav role="navigation" aria-label="Main menu">`.
  - Each menu item is a `<a>` or `<span>` (if not clickable).
- **Mobile compatibility:**
  - Use a hamburger menu for small screens.
  - Use CSS media queries for responsive design.
  - Ensure keyboard navigation and ARIA attributes for toggling.

### 3. Page Layout
- **Header:**
  - Site title, navigation menu, and optional logo.
- **Main:**
  - Page content (converted from markdown).
- **Footer:**
  - License, credits, and additional links.

### 4. Styling Best Practices
- **CSS:**
  - Use separate CSS files for dark/light themes.
  - Use semantic HTML elements (`<header>`, `<nav>`, `<main>`, `<footer>`).
  - Ensure high contrast and readable fonts.
- **Accessibility:**
  - ARIA roles for navigation and toggles.
  - Focus indicators for keyboard users.
  - Sufficient color contrast.
- **Responsive Design:**
  - Mobile-first CSS.
  - Hamburger menu for navigation on small screens.
  - Flexible grid or flexbox layout.

### 5. Asset Handling
- **Images:**
  - Ensure images referenced in markdown are present and correctly linked.
  - Log missing images, do not halt build.
- **Static files:**
  - Organize CSS, JS, and images in `static/`.

### 6. Build Process Notes
- **Destructive build:**
  - Remove `build/` before each run.
- **Strict ordering:**
  - Use `toc:` for menu and file generation order.
- **Logging:**
  - Log all actions and errors.

---

## Recommended Implementation Order

1. **Create and finalize template files:**
   - `header.html`, `footer.html`, `page.html` with ARIA and placeholders.
2. **Write CSS for base, dark, and light themes:**
   - Ensure responsive and accessible design.
3. **Implement navigation menu logic:**
   - Generate menu from `toc:`, add ARIA and mobile support.
4. **Integrate templates into markdown-to-HTML conversion:**
   - Use header/footer in all pages.
5. **Test image and asset handling:**
   - Log missing assets.
6. **Validate accessibility and mobile compatibility:**
   - Keyboard navigation, screen reader support, responsive layout.
7. **Iterate and refine based on feedback.**

---

Ready to proceed! Let me know if you want to start with template files, CSS, or another step from the recommended order.
