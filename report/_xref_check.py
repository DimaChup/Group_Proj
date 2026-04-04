import re, os, glob

ref_pat = re.compile(r'\\ref\{([^}]+)\}')
label_pat = re.compile(r'\\label\{([^}]+)\}')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Collect all refs from sections/
refs = {}
for f in glob.glob('sections/*.tex'):
    with open(f, encoding='utf-8', errors='replace') as fh:
        content = fh.read()
    for m in ref_pat.finditer(content):
        key = m.group(1)
        refs.setdefault(key, []).append(os.path.basename(f))

# Collect all labels from sections/ and main.tex
labels = set()
label_files = {}  # label -> file
files_to_scan = glob.glob('sections/*.tex') + ['main.tex']
for f in files_to_scan:
    if not os.path.exists(f):
        continue
    with open(f, encoding='utf-8', errors='replace') as fh:
        content = fh.read()
    for m in label_pat.finditer(content):
        labels.add(m.group(1))
        label_files[m.group(1)] = os.path.basename(f)

# Find broken refs
broken = []
for key, files in sorted(refs.items()):
    if key not in labels:
        broken.append((key, files))

# Find unused labels
all_refs_keys = set(refs.keys())
if os.path.exists('main.tex'):
    with open('main.tex', encoding='utf-8', errors='replace') as fh:
        for m in ref_pat.finditer(fh.read()):
            all_refs_keys.add(m.group(1))

section_labels = set()
for f in glob.glob('sections/*.tex'):
    with open(f, encoding='utf-8', errors='replace') as fh:
        content = fh.read()
    for m in label_pat.finditer(content):
        section_labels.add(m.group(1))

unused = sorted(section_labels - all_refs_keys)

print(f'Total unique refs in sections/: {len(refs)}')
print(f'Total unique labels in sections/+main.tex: {len(labels)}')
print(f'Broken refs (no matching label): {len(broken)}')
print(f'Unused labels (never referenced): {len(unused)}')
print()

print('=== BROKEN REFS ===')
for key, files in broken:
    flist = ', '.join(sorted(set(files)))
    # Find near-match labels
    suffix = key.split(':')[-1]
    candidates = [l for l in labels if suffix in l and l != key][:3]
    hint = f'  -> possible: {candidates}' if candidates else ''
    print(f'  ref{{{key}}}  in  {flist}{hint}')

print()
print('=== UNUSED LABELS (fig/tab only, likely orphans) ===')
for l in unused:
    if l.startswith('fig:') or l.startswith('tab:'):
        print(f'  label{{{l}}}')

print()
print('=== UNUSED LABELS (sec/eq, informational) ===')
for l in unused:
    if l.startswith('sec:') or l.startswith('eq:') or l.startswith('app:'):
        print(f'  label{{{l}}}')
