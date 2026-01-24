Benchmarks
==========

This document summarizes micro-benchmarks used to validate recent vectorization
work in the metrics module.

Summary
-------

- IC (information coefficient): ~4-5x speedup on synthetic panels (example sizes used: 200x100 and 500x200).
- Coverage: ~20-30x speedup on the same synthetic panels.

Accuracy
--------

Unit tests and benchmarks compare the new vectorized implementations against
straightforward groupby.apply baselines; results are numerically identical
within floating point precision (max absolute differences observed ~1e-15).

Reproduce locally
-----------------

From the project root:

```bash
uv run python examples/benchmark_ic.py
```

Notes
-----

- Benchmarks are synthetic and intended as quick micro-benchmarks; real-world
  speedups may vary depending on data sparsity and hardware.
- Consider adding the benchmark script to CI or publishing benchmark results in
  a dedicated release note when shipping performance-oriented changes.
