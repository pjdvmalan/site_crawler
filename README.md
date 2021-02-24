
# Site Crawler - website performance checker

> Real User Monitoring (RUM) website performance analysis tool

[![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)](https://python.org)
[![GitHub tag](https://img.shields.io/github/tag/pjdvmalan/site_crawler?include_prereleases=&sort=semver)](https://github.com/pjdvmalan/site_crawler/releases/)
[![License - MIT](https://img.shields.io/badge/License-MIT-blue)](#license)

## Features

- List all URLs referenced in a site's `sitemap.xml` file.
- Report on page _resource_ and _performance_ metrics across a site, or single URL.

## Installation

### Clone

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
sudo apt-install python3
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

- Set your parameters in the new file.

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
|url|URL being analysed.|
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
- Location: `/var/{website_domain}/analysis_report_{timestamp}.csv`

### 2. Resource References

| Attribute | Description |
|--------|-------------|
|url|The resource URL that was called by a page.|
|type|The resource type: image, font, CSS, JavaScript, etc. |
|cnt|The total number of times this resource was loaded accross all pages processed.|

NOTES:

- Location: `/var/{website_domain}/resource_references_report_{timestamp}.csv`

## Resources

- [Window.performance](https://www.w3.org/TR/navigation-timing/#sec-navigation-timing-interface)
- [Navigation Timing](https://www.w3.org/TR/navigation-timing)
- [PerformanceEntry Types](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceEntry/entryType)
- [PerformanceResourceTiming](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming)
- [Using the Resource Timing API](https://developer.mozilla.org/en-US/docs/Web/API/Resource_Timing_API/Using_the_Resource_Timing_API)
- [PerformancePaintTiming](https://developer.mozilla.org/en-US/docs/Web/API/PerformancePaintTiming)
- [PerformanceNavigationTiming](https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming)
- https://developers.google.com/speed/docs/insights/v5/get-started

## Contributing

Contributions welcome! Contributing to open source projects is a great way to learn more about:

- Social coding on GitHub.
- Get involved in technologies new to you.

### How to make a clean pull request

- Create a personal fork of this project on GitHub.
- Clone the fork on your local machine. Your remote repo on GitHub is called `origin`.
- Add the original repository as a remote called `upstream`.
- If you created your fork a while ago be sure to pull upstream changes into your local repository.
- Create a new branch to work on. Branch from `main`.
- Implement your new feature, or fix a bug. Remember to comment your code.
- Follow the code style of the project, including indentation.
- Add or change the documentation as needed.
- Squash your commits into a single commit with git's [interactive rebase](https://help.github.com/articles/interactive-rebase). Create a new branch if necessary.
- Push your branch to your fork on GitHub, the remote `origin`.
- From your fork open a pull request in the correct branch. Target the project's `main` branch.
- If the PR requires changes, push them to your branch. The PR will be updated automatically.
- Once the pull request is approved and merged you can pull the changes from `upstream` to your local repo and delete any redundant local branches.

And last but not least: Always write your commit messages in the present tense. Your commit message should describe what the commit, when applied, does to the code – not what you did to the code.

## License

Released under [MIT](/LICENSE) by [@pjdvmalan](https://github.com/pjdvmalan).
