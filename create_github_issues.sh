#!/bin/zsh
# create_github_issues.sh
# Automates creation of colored labels and issues for conversion workflow

# --- Label definitions ---
gh label create "conversion:markdown-patching" --color FFD700 --description "Robust Markdown image reference patching using DB mapping"
gh label create "conversion:docx-output" --color 00BFFF --description "Ensure DOCX output uses absolute paths and creates output directory"
gh label create "db:update-markdown-entry" --color 32CD32 --description "Fix DB update for Markdown entries"
gh label create "ui:admin-enhancements" --color FF69B4 --description "Add checkmark/ex display and search/filtering to admin UI"
gh label create "automation:github-issues" --color FFA500 --description "Automate GitHub issue creation for conversion workflows and admin UI"
gh label create "conversion:robustness" --color 8A2BE2 --description "Ensure all conversions update DB and handle errors robustly"

# --- Issue creation ---
gh issue create \
  --title "[conversion:markdown-patching] Robust Markdown image reference patching using DB mapping" \
  --label "conversion:markdown-patching" \
  --body - <<EOF
Update \`patch_markdown_with_db\` and \`update_image_refs_in_markdown\` in \`oerforge/convert.py\` to ensure robust, non-destructive image reference patching using the database mapping. Only overwrite original files if replacements are made.

**Tag:** <span style="color:#FFD700;">conversion:markdown-patching</span>
EOF

gh issue create \
  --title "[conversion:docx-output] Ensure DOCX output uses absolute paths and creates output directory" \
  --label "conversion:docx-output" \
  --body - <<EOF
Update \`md_to_docx\` in \`oerforge/convert.py\` to use absolute output paths, create output directory if missing, and update DB flags for successful conversion.

**Tag:** <span style="color:#00BFFF;">conversion:docx-output</span>
EOF

gh issue create \
  --title "[db:update-markdown-entry] Fix DB update for Markdown entries" \
  --label "db:update-markdown-entry" \
  --body - <<EOF
Ensure \`md_to_docx\` and related DB helpers in \`oerforge/convert.py\` correctly update the database for Markdown conversions, avoiding warnings for missing entries.

**Tag:** <span style="color:#32CD32;">db:update-markdown-entry</span>
EOF

gh issue create \
  --title "[ui:admin-enhancements] Add checkmark/ex display and search/filtering to admin UI" \
  --label "ui:admin-enhancements" \
  --body - <<EOF
Enhance admin UI scripts (e.g., \`oerforge_admin/viewdb.py\`) to display conversion status with checkmarks/exes and implement search/filtering for pages and images.

**Tag:** <span style="color:#FF69B4;">ui:admin-enhancements</span>
EOF

gh issue create \
  --title "[automation:github-issues] Automate GitHub issue creation for conversion workflows and admin UI" \
  --label "automation:github-issues" \
  --body - <<EOF
Create a script or workflow to automate GitHub issue creation for new conversion features and admin UI improvements, using colored tags for categorization.

**Tag:** <span style="color:#FFA500;">automation:github-issues</span>
EOF

gh issue create \
  --title "[conversion:robustness] Ensure all conversions update DB and handle errors robustly" \
  --label "conversion:robustness" \
  --body - <<EOF
Update conversion functions in \`oerforge/convert.py\` and \`build.py\` to ensure all conversions (Markdown, DOCX, PDF, TeX) update the DB correctly and provide diagnostic output and error handling.

**Tag:** <span style="color:#8A2BE2;">conversion:robustness</span>
EOF