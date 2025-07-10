"""
build_footer_html.py

Script to generate the validated footer HTML from _content.yml using the template in static/templates/footer.html.
- Loads _content.yml and validates the footer section using content_parser.py
- Renders the footer.html template with the YAML footer text
- Prints the HTML to stdout

Usage:
    python build_footer_html.py > footer.html
"""
from content_parser import load_and_validate_content_yml
import os

TEMPLATE_PATH = os.path.join('static', 'templates', 'footer.html')

def render_footer(footer_text):
    with open(TEMPLATE_PATH, 'r') as f:
        template = f.read()
    return template.replace('{{ footer_text }}', footer_text)

if __name__ == '__main__':
    content = load_and_validate_content_yml('_content.yml')
    footer_text = content['footer']['text']
    html = render_footer(footer_text)
    print(html.strip())
