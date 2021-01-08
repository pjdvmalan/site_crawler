# Site Crawler - website performance checker

Real user monitoring (RUM) website performance analysis tool.

## Features

- List all URLs referenced in a site's site.xml.
- Bootstrap a site's cache.
- Report on page performance metrics.

## Installation

- `brew install geckodriver` (for Firefox)
- `python3 -m venv venv`
- `. venv/bin/activate`
- `pip install -r requirements.txt` (or `requirements-dev.txt` in development).
- Copy `config_local_template.py`, name it `config_local.py` and update the parameters.

## Usage

Execute `./crawl_site.py -h` for help.

## Metrics

![alt text](https://www.w3.org/TR/navigation-timing/timing-overview.png)

|  Measure (s) | Attribute | Attribute | Summary |
| ------------- | ------------- | ------------- | ------------- |
| Total | loadEventStart | navigationStart | The time taken for the page to load, from clicking on the link until fully loaded in the browser. |
| Data transfer | responseEnd | responseStart | The time taken to download the page, from first byte received, to last. |
| Latency | responseStart | fetchStart | How long it takes the response to get to to the browser. This includes the time it takes for the request to get to the server, the time it takes the server to render a response, and the time until the first byte of that response gets back to the browser. |
| Rediretion | redirectEnd | redirectStart | Overhead that is added by HTTP redirects. |
| White Screen | responseStart | navigationStart |  |
| DOM Rendering | domComplete | domLoading |  |
| Request | responseEnd | requestStart |  |
| DOM Interactive | domComplete | domInteractive |  |

## Resources

- [Navigation Timing](https://www.w3.org/TR/navigation-timing)

## License

Released under [MIT](/LICENSE).
