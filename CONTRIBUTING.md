# Contributing to bagel-factor

Thank you for considering contributing to bagel-factor! This document outlines the development workflow and guidelines.

## Development Setup

### Prerequisites

- Python >=3.12
- [`uv`](https://github.com/astral-sh/uv) for dependency management

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/bagelquant/bagel-factor.git
cd bagel-factor

# Install dependencies
uv sync

# Verify installation
uv run pytest tests/
```

## Development Workflow

### Running Tests

```bash
# Run all tests
uv run pytest tests/

# Run with verbose output
uv run pytest tests/ -v

# Run specific test file
uv run pytest tests/test_metrics_module.py

# Run specific test
uv run pytest tests/test_metrics_module.py::test_icir_basic
```

### Code Style

We use **Ruff** for both linting and formatting.

```bash
# Format code
uv run ruff format src/ tests/

# Check linting
uv run ruff check src/ tests/

# Fix auto-fixable issues
uv run ruff check src/ tests/ --fix
```

**Before committing**:
1. Run `uv run ruff format src/ tests/`
2. Run `uv run ruff check src/ tests/`
3. Run `uv run pytest tests/`

All three must pass!

### Making Changes

1. **Create a branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**:
   - Follow existing code style and patterns
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes**:
   ```bash
   uv run pytest tests/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```

   Commit message format:
   - `feat: Add new feature`
   - `fix: Fix bug in IC calculation`
   - `docs: Update README`
   - `test: Add tests for quantiles`
   - `refactor: Simplify panel validation`

5. **Push and create a Pull Request**:
   ```bash
   git push origin your-branch-name
   ```

## Pull Request Guidelines

### Before Submitting

- [ ] All tests pass (`uv run pytest tests/`)
- [ ] Code is formatted (`uv run ruff format`)
- [ ] Linting passes (`uv run ruff check`)
- [ ] Added tests for new functionality
- [ ] Updated documentation if needed
- [ ] PR description explains what and why

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Changes Made
- List key changes

## Testing
- Describe how you tested
- List new tests added

## Checklist
- [ ] Tests pass
- [ ] Ruff format applied
- [ ] Ruff linting passes
- [ ] Documentation updated
```

## Adding New Features

### API Design Principles

1. **Pandas-first**: Work with DataFrame/Series as primary data structures
2. **Explicit over implicit**: Require users to prepare data correctly
3. **Single responsibility**: Each function does one thing well
4. **Composable**: Functions work well together
5. **No surprises**: Behavior should be predictable

### Code Organization

- **src/bagelfactor/data/**: Data loading and panel operations
- **src/bagelfactor/metrics/**: Factor evaluation metrics (IC, quantiles, etc.)
- **src/bagelfactor/preprocess/**: Data transformations (ZScore, Rank, etc.)
- **src/bagelfactor/stats/**: Statistical tests
- **src/bagelfactor/visualization/**: Plotting functions
- **src/bagelfactor/single_factor/**: Main evaluation job
- **src/bagelfactor/utils/**: Optional utilities

### Adding a New Metric

1. Create the function in appropriate module (e.g., `metrics/new_metric.py`)
2. Add to module's `__init__.py` imports and `__all__`
3. Add to main `__init__.py` imports and `__all__`
4. Write tests in `tests/test_metrics_module.py`
5. Add documentation in `docs/modules/metrics/`

## Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions in isolation
- **Integration tests**: Test workflows (e.g., `SingleFactorJob.run()`)
- **Edge cases**: Empty data, single values, all NaN, etc.

### Writing Tests

```python
def test_function_name() -> None:
    """Test description."""
    # Arrange: Set up test data
    panel = _create_test_panel()
    
    # Act: Call function
    result = my_function(panel)
    
    # Assert: Verify results
    assert result.loc[...] == pytest.approx(expected_value)
```

### Test Data

Use small, deterministic test data. See existing tests for examples.

## Documentation

### Docstring Style

We use NumPy-style docstrings:

```python
def my_function(panel: pd.DataFrame, factor: str, n_quantiles: int = 5) -> pd.Series:
    """Brief one-line description.

    Longer description if needed. Explain what the function does,
    not how it does it.

    IMPORTANT: Note any critical requirements (e.g., sorted data).

    Parameters
    ----------
    panel : pd.DataFrame
        Panel indexed by (date, asset)
    factor : str
        Column name for factor
    n_quantiles : int, default 5
        Number of quantiles

    Returns
    -------
    pd.Series
        Quantile assignments indexed by (date, asset)

    Examples
    --------
    >>> panel = ensure_panel_index(df)
    >>> q = my_function(panel, factor='alpha')
    """
```

### Adding Documentation

- Update relevant `docs/modules/` files
- Add examples to docstrings
- Update README if changing public API

## Philosophy & Design

Remember that bagel-factor is a **precision calculation engine**:

- **User's responsibility**: Data preparation, sorting, point-in-time integrity
- **Package's responsibility**: Accurate calculations, NaN handling, clear errors

Document requirements clearly but don't over-validate.

## Questions?

- **Issues**: https://github.com/bagelquant/bagel-factor/issues
- **Discussions**: https://github.com/bagelquant/bagel-factor/discussions
- **Email**: eric.yanzhong.huang@gmail.com

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
