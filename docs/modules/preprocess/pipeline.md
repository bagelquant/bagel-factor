# `bagelfactor.preprocess.pipeline`

Fit/transform pipeline.

## `Transform` (protocol-like base class)

Internal base type for pipeline steps.

### `fit(panel) -> Transform`
- Default implementation returns `self`.
- In v0 most transforms are stateless and only implement `transform`.

### `transform(panel) -> pd.DataFrame`
- Must be implemented by subclasses.

## `Pipeline(steps)`

A small pipeline that applies a sequence of `Transform` steps.

### Construction
```python
from bagelfactor.preprocess import Pipeline, Clip, ZScore, Rank

pp = Pipeline([Clip("alpha", lower=-3, upper=3), ZScore("alpha"), Rank("alpha")])
```

### Attributes
- `steps: tuple[Transform, ...]`

### Methods

#### `fit(panel) -> Pipeline`
Calls `step.fit(panel)` then `step.transform(panel)` sequentially, updating the intermediate panel.

#### `transform(panel) -> pd.DataFrame`
Applies `step.transform(...)` sequentially.

#### `fit_transform(panel) -> pd.DataFrame`
Equivalent to `fit(panel)` followed by `transform(panel)`.

### Notes
- Pipeline does not validate panel shape; individual transforms typically validate via `validate_panel`.
- Steps are stored as an immutable tuple.
