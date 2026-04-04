# Karpathy's Autoresearch

## Repo

**URL**: https://github.com/karpathy/autoresearch
**Stars**: ~53k (as of March 2026)
**License**: MIT

## What It Does

An autonomous ML experiment loop. You point an AI coding agent (e.g. Claude, Cursor, Copilot) at the repo, and it:

1. Reads `program.md` (your research instructions)
2. Modifies `train.py` (GPT model + optimizer + training loop)
3. Runs a 5-minute training experiment on a single GPU
4. Checks if `val_bpb` (validation bits per byte) improved
5. Keeps the change if better, discards if worse
6. Repeats autonomously

You wake up to ~100 experiments overnight, each with a git commit showing what was tried and whether it helped. No human input needed after launch.

## Requirements

- **GPU**: Single NVIDIA GPU (tested on H100, smaller GPUs work with reduced settings)
- **Python**: 3.10+
- **Package manager**: `uv` (https://docs.astral.sh/uv/)

## Setup

```bash
git clone https://github.com/karpathy/autoresearch.git
cd autoresearch

# Install uv if needed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Prepare data + tokenizer (~2 min)
uv run prepare.py

# Manual test run (~5 min, verify everything works)
uv run train.py
```

## Running

Point your AI agent at the repo and say:

> "Have a look at program.md and let's kick off a new experiment."

The agent will autonomously modify `train.py`, run experiments, and iterate.

## File Structure

| File | Who edits it | Purpose |
|------|-------------|---------|
| `program.md` | You (human) | Research directions, instructions for the agent |
| `train.py` | Agent | GPT model, optimizer, training loop (the thing being improved) |
| `prepare.py` | Nobody | Data prep, tokenizer, utilities (fixed) |
| `pyproject.toml` | Nobody | Dependencies |

## Key Design Choices

- **Fixed 5-min time budget** per experiment (wall clock, excluding startup). Fair comparison across changes. ~12 experiments/hour.
- **Single file** modified (`train.py`). Keeps diffs reviewable.
- **val_bpb metric** (lower = better, vocab-size-independent).
- **Git history** records every experiment attempt and result.

## For Smaller GPUs

Reduce these in `train.py`:
- `DEPTH` (fewer transformer layers)
- `MAX_SEQ_LEN` (shorter sequences)
- `TOTAL_BATCH_SIZE` (smaller batches)
- Use smaller datasets like TinyStories

## Platform Notes

- NVIDIA GPU only out of the box
- Community forks exist for: MacOS (MLX), Windows (RTX), AMD
- No CPU/MPS support in the main repo

## Why It Matters

Shopify CEO ran it on their templating engine and got 53% faster rendering from 93 automated commits. The pattern (agent + metric + loop) is generalizable beyond ML training to any codebase with a measurable objective.
