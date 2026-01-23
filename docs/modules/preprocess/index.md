# `bagelfactor.preprocess` (module index)

Lightweight, pandas-first preprocessing utilities used by single-factor evaluation.

## Public API

```python
from bagelfactor.preprocess import (
    Pipeline,
    DropNa,
    Clip,
    ZScore,
    Rank,
)
```

## Notes
- All transforms operate on canonical panels indexed by `(date, asset)`.
- Transforms are applied **cross-sectionally** per `date` when applicable.
