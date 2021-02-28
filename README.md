
# Site Crawler - website performance checker

> Real User Monitoring (RUM) website performance analysis tool

[![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)](https://python.org)
[![GitHub tag](https://img.shields.io/github/tag/pjdvmalan/site_crawler?include_prereleases=&sort=semver)](https://github.com/pjdvmalan/site_crawler/releases/)
[![License - MIT](https://img.shields.io/badge/License-MIT-blue)](#license)

## Features

This tool aims to answer the following questions:

1. What is the performance of my website?

2. What external websites am I linking too?

3. What resources are being used, e.g. CSS, JS, images, fonts, etc.

4. Are there any dead links being used in my site?

## Installation

### Clone the repository

```sh
git clone git@github.com:pjdvmalan/site_crawler.git
cd site_crawler
```

### Install system dependencies

Install Firefox - see the [download](https://www.mozilla.org/en-US/firefox/new/) page.

Install Firefox's webdriver:

```sh
# macOS
brew install geckodriver

# Debian/Ubuntu
sudo apt-get update
sudo apt-get install firefox-geckodriver
```

Install Python 3:

```sh
# macOS
brew install python@3

# Debian/Ubuntu
sudo apt-get update
sudo apt-get install python3
```

### Install project packages

Create a virtual environment in the repo. Activate it whenever install packages into it or running this project.

```sh
python3 -m venv venv
source venv/bin/activate
```

Install production dependencies:

```sh
pip install -r requirements.txt
```

Or, install prod and dev dependencies at once:

```sh
pip install -r requirements-dev.txt
```

### Configure

- Create local config.

    ```sh
    cp etc/config_local_template.py etc/config_local.py
    ```

- Set parameters in the new file.

- Obtain a [Google PageSpeed Insights API Key](https://developers.google.com/speed/docs/insights/v5/get-started).

## Usage

Run commands inside the virtual environment.

The project entrypoint is [site_crawler.py](/site_crawler.py).

To print help, run:

```sh
./crawl_site.py -h
```

NOTE: There are PageSpeed Insights API Limits, which is accomodated for in the code.

## Reports

Lighthouse metrics based on the following: [Performance Audits](https://web.dev/lighthouse-performance/).

### 1. Page Load Metrics

| Metric | Description |
|--------|-------------|
|time|Timestamp when measurement was taken.|
|url|URL being analysed.||
|performance||
|accessibility||
|best_practices||
|seo||
|first_contentful_paint||
|first_contentful_paint_score||
|speed_index||
|speed_index_score||
|largest_contentful_paint| The render time of the largest image or text block visible within the viewport.|
|largest_contentful_paint_score||
|interactive||
|interactive_score||
|total_blocking_time||
|total_blocking_time_score||
|cumulative_layout_shift||
|cumulative_layout_shift_score||
|third_party_wasted||
|third_party_wasted_size||
|grouping|The grouping assigned to thie URL.|
|server|Server responese time.|
|browser|Browser processing time.|
|usable|Time until the page is usable.|
|total|Total time taken for DOM rendering to complete.|
|data_transfer|Time taken for all synchronous data to load.|
|redirected|Time spend handling redirection.|
|dom|Time from DOM loading start, until DOM rendering completed.|
|fcp|First Meaningful Paint (FMP). Time taken for the above-the-fold layout change has happened and web fonts have loaded. It is when the answer to "Is the page useful?" becomes "yes".|
|img|Number of images loaded by this page.|
|img_sec|Duration.|
|img_size|Size.|
|css|Number of CSS files loaded by this page.|
|css_sec|Duration.|
|css_size|Size.|
|script|Number of script files loaded by this page.|
|script_sec|Duration.|
|script_size|Size.|
|font|Number of font files loaded by this page.|
|font_sec|Duration.|
|font_size|Size.|
|xhrt|Number of XHRT requests made by this page.|
|xhrt_sec|Duration.|
|xhrt_size|Size.|

NOTES:

- Time in seconds.
- Size in kilobytes.
- Location: `/var/{website_domain}/date/analysis_report_{timestamp}.csv`

### 2. Resource References

| Attribute | Description |
|--------|-------------|
|url|The resource URL that was called by a page.|
|type|The resource type: image, font, CSS, JavaScript, etc. |
|cnt|The total number of times this resource was loaded accross all pages processed.|

NOTES:

- Location: `/var/{website_domain}/resource_references_report_{timestamp}.csv`

## Resources

- Web Vitals
  - [What is web vitals?](https://web.dev/vitals/)
  - [Overview of tools to measure Core Web Vitals.](https://web.dev/vitals-tools/)
  - [Get Started with the PageSpeed Insights API.](https://developers.google.com/speed/docs/insights/v5/get-started)
  - [Google PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed).

- Windows Navigation Timing
  - [Navigation Timing](https://www.w3.org/TR/navigation-timing)
  - [PerformanceEntry Types](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceEntry/entryType)
  - [PerformanceResourceTiming](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming)
  - [Using the Resource Timing API](https://developer.mozilla.org/en-US/docs/Web/API/Resource_Timing_API/Using_the_Resource_Timing_API)
  - [PerformanceNavigationTiming](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming)

## Contributing

Contributions welcome! Contributing to open source projects is a great way to learn more about:

- Social coding on GitHub.
- Get involved in technologies new to you.

## License

Released under [MIT](/LICENSE) by [@pjdvmalan](https://github.com/pjdvmalan).

https://www.debugbear.com/blog/why-is-my-lighthouse-score-different-from-pagespeed-insights
https://pagespeedplus.com/blog/pagespeed-insights-vs-lighthouse
https://stackoverflow.com/questions/60153823/why-google-speed-insights-google-lighthouse-web-dev-showing-different-audit
https://medium.com/@OPTASY.com/google-pagespeed-vs-lighthouse-how-are-they-different-and-which-tool-should-you-use-3f03270c674
