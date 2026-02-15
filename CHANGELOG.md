# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Ruff for linting and formatting
- GitHub Actions CI workflow (tests on Python 3.12 and 3.13)
- Explicit `__all__` exports for better IDE support
- CONTRIBUTING.md with development guidelines
- CHANGELOG.md
- README badges (CI status, PyPI, Python versions, license)
- Optional validation utilities (`diagnose_panel()` function)
- Comprehensive data format requirements documentation

### Changed
- Replaced wildcard imports with explicit imports in main `__init__.py`
- Enhanced docstrings with precondition warnings for critical functions

### Fixed
- **ICIR calculation now uses sample std (ddof=1) instead of population std (ddof=0)**
  - This aligns with standard statistical practice
  - ICIR values will be slightly different from previous versions

## [0.1.3] - 2024-XX-XX

### Added
- Comprehensive module-level documentation
- Factor evaluation guide
- End-to-end examples with expected outputs
- Benchmarking scripts and documentation

### Changed
- Documentation structure reorganized for clarity
- Improved docstrings across all modules

## [0.1.2] - 2024-XX-XX

### Changed
- **Performance improvements**: Vectorized IC and coverage calculations
  - IC: 4-5x speedup
  - Coverage: 20-30x speedup
  - Numerical accuracy maintained

## [0.1.1] - 2024-XX-XX

### Added
- Statistical tests module (`bagelfactor.stats`)
  - `ttest_1samp`, `ttest_ind` for hypothesis testing
  - `ols_alpha_tstat`, `ols_summary` for regression analysis
- Visualization module (`bagelfactor.visualization`)
  - IC time series and histograms
  - Quantile returns plots
  - Long-short strategy plots
  - Turnover analysis plots
  - Coverage visualization
  - Multi-panel summary figure (`plot_result_summary`)
- Detailed module documentation in `docs/modules/`

### Fixed
- Matplotlib dependency made required (was optional, causing import errors)
- RangeIndex handling in regression functions
- Finite value filtering in statistical tests

## [0.1.0] - 2024-XX-XX

Initial release.

### Added
- Core data layer (`bagelfactor.data`)
  - Panel index operations (`ensure_panel_index`, `validate_panel`)
  - Forward returns calculation (`add_forward_returns`)
  - Calendar alignment with `exchange-calendars`
  - Data loaders for CSV, JSON, Excel, Parquet, Pickle
  - Factor and universe abstractions
- Metrics module (`bagelfactor.metrics`)
  - Information Coefficient (IC) and ICIR
  - Quantile assignment and returns
  - Turnover calculation
  - Coverage analysis
- Preprocessing module (`bagelfactor.preprocess`)
  - Pipeline pattern for chaining transforms
  - Transforms: Clip, ZScore, Rank, DropNa
- Single-factor evaluation (`bagelfactor.single_factor`)
  - `SingleFactorJob` for complete factor analysis
  - `SingleFactorResult` dataclass for results
- Reporting module (`bagelfactor.reporting`)
  - Export to CSV and Parquet
- Comprehensive test suite (48 tests)
- Documentation with examples

[Unreleased]: https://github.com/bagelquant/bagel-factor/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/bagelquant/bagel-factor/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/bagelquant/bagel-factor/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/bagelquant/bagel-factor/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/bagelquant/bagel-factor/releases/tag/v0.1.0
