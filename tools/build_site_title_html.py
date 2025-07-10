"""
build_site_title_html.py

Script to generate the site title/logo HTML block as seen in index.html, using content_parser.py for config.
- Reads _content.yml via content_parser.load_and_validate_content_yml
- Outputs the <header> HTML block with logo and title, matching the markup and inline styles in index.html
- Prints the HTML to stdout

Usage:
    python build_site_title_html.py > site_title.html
"""
from content_parser import load_and_validate_content_yml
import os

if __name__ == '__main__':
    content = load_and_validate_content_yml('_content.yml')
    site = content['site']
    # Extract logo, title, and description
    logo = site['logo']
    title = site['title']
    description = site.get('description', '')
    # The logo path in index.html is ./images/logo.png, but in YAML it's static/images/logo.png
    # We'll strip 'static/' and prepend './' for parity
    logo_web = './' + logo[len('static/'):] if logo.startswith('static/') else logo
    html = f'''
  <header class="site-header" style="display: flex; flex-direction: column; align-items: center; gap: 0.7em;">
    <div style="display: flex; align-items: center; justify-content: center; gap: 1.2em; width: 100%;">
      <img src="{logo_web}" alt="Site logo" class="site-logo" style="height: 80px; width: 80px; border-radius: 18px; object-fit: cover;" />
      <div style="display: flex; flex-direction: column; align-items: flex-start; justify-content: center;">
        <h1 class="site-title" style="margin: 0; text-align: center; font-size: 3em; font-weight: 800; letter-spacing: -1.5px;">{title}</h1>
        <div class="site-subtitle" style="margin: 0; text-align: center; font-size: 1.2em; font-weight: 400; color: #666; max-width: 32em;">{description}</div>
      </div>
    </div>
  </header>
'''
    print(html.strip())
