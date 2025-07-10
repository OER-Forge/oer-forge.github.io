import yaml

toc = yaml.safe_load(open('_toc.yml'))
chapters = toc.get('chapters', [])
if not chapters:
    print('[ERROR] No chapters found in TOC.')
    exit(1)
first = chapters[0]
if 'file' in first:
    print(f"[OK] First chapter is a file: {first['file']}")
else:
    print(f"[ERROR] First chapter is not a file. It is: {list(first.keys())}")
    exit(1)
