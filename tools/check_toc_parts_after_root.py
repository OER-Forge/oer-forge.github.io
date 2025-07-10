import yaml

toc = yaml.safe_load(open('_toc.yml'))
chapters = toc.get('chapters', [])
if len(chapters) < 2:
    print('[WARN] Less than two chapters in TOC.')
    exit(0)
for i, ch in enumerate(chapters[1:], 2):
    if 'part' not in ch:
        print(f"[ERROR] Chapter {i} after root is not a part: {ch}")
        exit(1)
print('[OK] All chapters after the root are parts.')
