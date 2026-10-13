# Password Search-Space Calculator

This script calculates:
- `alphabet_size ** unknown_positions`
- theoretical full-search duration from a measured candidate-check rate
- a simple average-position estimate (half of the full-search time)

## Run
From the repository root:

```bash
python3 analysis/password_analysis.py
```

Enter a rate measured in your own authorized lab. Do not assume a rate from another computer or tool version applies to your system.

## Scope and limitations
The script does **not** generate password candidates, inspect captures, or attempt authentication. It performs arithmetic only. Its estimates assume a constant rate and a uniformly located correct candidate; real search behavior may differ.
