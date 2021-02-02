# Site Crawler - website performance checker
> Real user monitoring (RUM) website performance analysis tool

[![Python](https://img.shields.io/badge/Python-3-blue?logo=python&logoColor=white)](https://python.org)
[![GitHub tag](https://img.shields.io/github/tag/pjdvmalan/site_crawler?include_prereleases=&sort=semver)](https://github.com/pjdvmalan/site_crawler/releases/)
[![License - MIT](https://img.shields.io/badge/License-MIT-blue)](#license)

## Features

- List all URLs referenced in a site's `sitemap.xml` file.
- Bootstrap a site's cache.
- Report on page performance metrics using the browser's builtin metrics on `window.performance`

## Installation

### Clone

```sh
git clone git@github.com:pjdvmalan/site_crawler.git
cd site_crawler
```

### Install system dependencies

Install Firefox - see [Download](https://www.mozilla.org/en-US/firefox/new/) page.

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
- Set your parameters in the new file.

## Usage

Run commands inside the virtual environment.

The project entrypoint is [site_crawler.py](/site_crawler.py).

To print help, run:

```sh
./crawl_site.py -h
```

## Metrics

![Timing overview](https://www.w3.org/TR/navigation-timing/timing-overview.png)

Metrics reported on in this project are shown below, ordered from focusing on the start of the page load sequence to focusing on the end.

| Metric          | End event        | Start event       | Summary                                                                                                                                                                                                                                                        |
| --------------- | ---------------- | ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Total           | `loadEventStart` | `navigationStart` | The time taken for the page to load, from clicking on the link until fully loaded in the browser.                                                                                                                                                              |
| Redirection     | `redirectEnd`    | `redirectStart`   | Overhead that is added by HTTP redirects.                                                                                                                                                                                                                      |
| White Screen    | `responseStart`  | `navigationStart` |                                                                                                                                                                                                                                                                |
| Data transfer   | `responseEnd`    | `responseStart`   | aka "Request response time". The time taken to download the page, from first byte to last byte received.                                                                                                                                                                                        |
| Latency         | `responseStart`  | `fetchStart`      | How long it takes the response to get to to the browser. This includes the time it takes for the request to get to the server, the time it takes the server to render a response, and the time until the first byte of that response gets back to the browser. |
| Request         | `responseEnd`    | `requestStart`    |                                                                                                                                                                                                                                                                |
| Page Rendering   | `domComplete`    | `domLoading`      |                                                                                                                                                                                                                                                                |
| Time to interactive | `domInteractive`    | `navigationStart`  |                                                                                                                                                                                                                                                                |

## Resources

- [Window.performance](https://developer.mozilla.org/en-US/docs/Web/API/Window/performance) in Mozilla dev docs.
- [Navigation Timing](https://www.w3.org/TR/navigation-timing)

## License

Released under [MIT](/LICENSE) by [@pjdvmalan](https://github.com/pjdvmalan).
