# Federal Crime Data Standardization and Analysis

### [*Click here for a detailed description of the data sources, methodology, and findings*](https://www.documentcloud.org/documents/5692683-Methodology-for-National-Analysis-of-Clearance.html)

This repository includes methodologies, data, and code supporting the following articles, published by The Trace and BuzzFeed News:

- "Shoot Someone In A Major US City, And Odds Are You’ll Get Away With It" (January 24, 2019) — [The Trace](https://www.thetrace.org/features/murder-solve-rate-gun-violence-baltimore-shootings) / [BuzzFeed News](https://www.buzzfeednews.com/article/sarahryley/police-unsolved-shootings)
- "5 Things To Know About Cities’ Failure To Arrest Shooters" (January 24, 2019) — [The Trace](https://www.thetrace.org/2019/01/gun-murder-solve-rate-understaffed-police-data-analysis) / [BuzzFeed News](https://www.buzzfeednews.com/article/sarahryley/5-things-to-know-about-cities-failure-to-arrest-shooters)

[*Click here for additional data and code from The Trace and BuzzFeed News's collaboration.*](https://github.com/the-trace-and-buzzfeed-news/introduction)

# Raw Data

The analysis is based, primarily, on three major datasets collected and published by the Federal Bureau of Investigation (FBI): Return A data, Supplementary Homicide Report data, and the National Incident-Based Reporting System. Each serves different purposes (for the FBI, and for our analyses), and each has different benefits and drawbacks. A detailed explanation of each can be found in the methodology linked above.

The FBI's raw data files require many gigabytes of storage in total, and so are not directly included in this repository. The Trace and BuzzFeed News have [uploaded the raw files to the Internet Archive](https://archive.org/details/fbi-raw-data-files-nibrs-shr-return-a), where you can download them. 

# Standardized Data

The raw Return A, NIBRS, and SHR data are formatted entirely differently from one another, use different terminology, different variables, and different data structures. To facilitate the combination and comparison of these three datasets, The Trace and BuzzFeed News created "standardized" versions of them all. You can find the standardized data in the [`data/standardized`](data/standardized) directory, and data dictionary of the standardized datasets in the [`documentation/`](documentation/) folder.

The code to standardize the raw data can be found in the three Jupyter notebooks, written in the Python programming language, in the `notebooks/standardize` directory. Each notebook processes one of the three main federal datasets, and saves a standardized version to the `data/standardized` directory.


# Data and Analysis

The code to analyze the standardized data can be found in the four Jupyter notebooks, written in the Python programming language, in the `notebooks/analyze` directory. Each of the first three notebooks analyzes one of the three federal datasets; the fourth compares findings from the three datasets to one another. The findings are also summarized in the methodology linked in the first section of this document.

# Reproducibility

Executing the notebooks above, in order, will reproduce the findings. You will need Python 3 installed, as well as the Python libraries specified in this repository's `Pipfile`.

Before running the standardization code, you will need to download the raw data files from the Internet Archive, and place them in the `data/raw` directory, so that that folder's structure becomes:

```
data/
    raw/
        nibrs/
        reta/
        shr/
```

You do not need to run the standardization code (which can take several hours to finish) in order to run the analysis code. But if you choose not to run the standardization code, you will first need to unzip the `data/standardized/nibrs-victims.csv.zip` and `data/standardized/nibrs-victims.csv.zip` files in order for the analysis to work.


# Licensing

All code in this repository is available under the [MIT License](https://opensource.org/licenses/MIT). The standardized data files are available under the [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) (CC BY 4.0) license.

# Questions / Feedback

For questions or feedback, please contact Jeremy Singer-Vine ([jeremy.singer-vine@buzzfeed.com](jeremy.singer-vine@buzzfeed.com)) and Sarah Ryley ([sryley@thetrace.org](sryley@thetrace.org)).
