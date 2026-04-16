#!/usr/bin/env bash
# Build D7 PDF from sources in this folder.
# Usage: ./build.sh (or `bash build.sh` on Windows)
set -e
cd "$(dirname "$0")"

echo "[D7] pdflatex pass 1"
pdflatex -interaction=nonstopmode main.tex > /dev/null

if [ -f references.bib ]; then
  echo "[D7] biber"
  biber main 2>/dev/null || true
fi

echo "[D7] pdflatex pass 2"
pdflatex -interaction=nonstopmode main.tex > /dev/null
echo "[D7] pdflatex pass 3"
pdflatex -interaction=nonstopmode main.tex > /dev/null

echo "[D7] rendering page PNGs"
pdftoppm -r 150 main.pdf page -png 2>/dev/null || echo "  (pdftoppm not installed — skipping PNGs)"

# --- Snapshot to pdf_versions/ with next version number ---
mkdir -p pdf_versions
next=$(( $(ls pdf_versions/ 2>/dev/null | grep -oE '^v[0-9]+' | grep -oE '[0-9]+' | sort -n | tail -1 || echo 0) + 1 ))
cp main.pdf "pdf_versions/v${next}.pdf"
echo "[D7] snapshot: pdf_versions/v${next}.pdf"

# --- Extract text and run AI-tell detection ---
echo "[D7] extracting text from PDF"
if command -v pdftotext &>/dev/null; then
  pdftotext main.pdf _body.txt
else
  python -c "
import fitz
doc = fitz.open('main.pdf')
with open('_body.txt','w',encoding='utf-8') as f:
    for p in doc: f.write(p.get_text())
"
fi

WORDCOUNT=$(wc -w < _body.txt)
echo "[D7] body word count: $WORDCOUNT"

echo "[D7] running AI-tell scanner"
python -c "
import re, sys

text = open('_body.txt', encoding='utf-8').read()
lower = text.lower()
lines = []

# AI transition words
transitions = ['furthermore', 'moreover', 'additionally']
t_count = sum(lower.count(w) for w in transitions)
lines.append(f'AI transitions (furthermore/moreover/additionally): {t_count}')

# AI hedging phrases
hedges = ['it is worth noting', 'it could be argued', 'this highlights']
h_count = sum(lower.count(h) for h in hedges)
lines.append(f'AI hedging phrases: {h_count}')

# not only... but also
noba = len(re.findall(r'not only\b.{1,80}\bbut also\b', lower))
lines.append(f'\"not only... but also\" patterns: {noba}')

# sentence stats
sentences = [s.strip() for s in re.split(r'\.\s', text) if len(s.strip()) > 5]
n_sent = len(sentences) if sentences else 1
avg_len = sum(len(s.split()) for s in sentences) / n_sent
lines.append(f'Sentences: {n_sent},  avg words/sentence: {avg_len:.1f}')

# verdicts
flags = 0
if t_count > 3:
    lines.append('  WARNING: >3 AI transition words')
    flags += 1
if h_count > 2:
    lines.append('  WARNING: >2 AI hedging phrases')
    flags += 1
if 18 <= avg_len <= 22:
    lines.append('  WARNING: avg sentence length in AI sweet spot (18-22)')
    flags += 1

if flags == 0:
    verdict = 'PASS'
elif flags == 1:
    verdict = 'WARNING'
else:
    verdict = 'FAIL'
lines.append(f'\nVERDICT: {verdict}')

report = '\n'.join(lines)
print(report)
with open('ai_check_report.txt', 'w') as f:
    f.write(f'Word count: $WORDCOUNT\n{report}\n')
"

echo ""
echo "=== DONE ==="
ls -lh main.pdf
echo ""
echo "Pages: $(pdfinfo main.pdf 2>/dev/null | grep Pages || python -c 'import fitz; print("Pages:", len(fitz.open(\"main.pdf\")))')"
echo "Snapshots:"
ls -1 pdf_versions/
echo ""
echo "AI check: ai_check_report.txt"
rm -f _body.txt
