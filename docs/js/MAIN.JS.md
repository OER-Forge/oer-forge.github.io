# MAIN.JS.md

This file documents the functionality of `static/js/main.js`, which provides interactive UI features for the main documentation page.

## Features

### Theme Toggle
- The theme toggle button (`#theme-toggle`) switches between light and dark CSS themes by updating the `href` of the theme stylesheet (`#theme-css`).
- The button icon and ARIA label update to reflect the current theme (🌙 for light, ☀️ for dark).
- The theme persists for the session (until page reload).

### Font Appearance Controls
- Font controls (radio buttons in `.font-controls`) allow users to select font family, size, letter spacing, and line height.
- Selections are saved to `localStorage` and applied on page load.
- Changes update CSS variables or the `font-family` property for the body, container, and markdown content.
- The selected radio button is checked on load to reflect saved preferences.

### Accessibility
- All controls are keyboard accessible and use ARIA labels for improved accessibility.
- Focus styles and persistent settings enhance usability for all users.

## Usage
- This script should be loaded only on the main documentation page.
- It expects the HTML template to include the theme toggle button, font controls, and the appropriate CSS classes/IDs.

## Example HTML Structure
```html
<link id="theme-css" rel="stylesheet" href="css/theme-light.css">
<div class="font-controls"> ... </div>
<button id="theme-toggle">🌙</button>
<div class="markdown-body"> ... </div>
```

## See Also
- `static/js/site.js` for site-wide accessibility and UI enhancements.
