import re
import sys

UNICODE_REPLACEMENTS = {
    "✅": "[Check]",
    "🚀": "[Rocket]",
    "μ": "mu",
    # Add more as needed
}

def sanitize_text(text):
    for uni, repl in UNICODE_REPLACEMENTS.items():
        text = text.replace(uni, repl)
    return text

if __name__ == "__main__":
    for fname in sys.argv[1:]:
        with open(fname, "r", encoding="utf-8") as f:
            content = f.read()
        new_content = sanitize_text(content)
        with open(fname, "w", encoding="utf-8") as f:
            f.write(new_content)