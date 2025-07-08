# Data module

This package uses the a multi-index DataFrame to store data, which is a common practice in quantitative finance. The DataFrame is indexed by date and Asset(ticker), allowing for efficient time-series operations and easy access to data for specific assets on specific dates.

This module offer the following functionalities:

- csv: read from csv file and return a standardized DataFrame
    - csv file must have column `date` and `ticker`
- bagel-tushare: read from local database following the structure of `bagel-tushare` package
    - more information can be found in the [bagel-tushare](https://github.com/bagelquant/bagel-tushare) repository
