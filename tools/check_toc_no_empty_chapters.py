import yaml

toc = yaml.safe_load(open('_toc.yml'))
def walk(node):
    if isinstance(node, dict):
        if 'chapters' in node and not node['chapters']:
            print(f"[ERROR] Empty chapters list in: {node}")
            exit(1)
        for k in ('chapters', 'sections'):
            if k in node:
                for c in node[k]: walk(c)
    elif isinstance(node, list):
        for c in node: walk(c)
walk(toc.get('chapters', []))
print('[OK] No empty chapters lists in TOC.')
