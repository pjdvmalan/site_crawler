# Site Crawler - website performance checker
> Real user monitoring (RUM) website performance analysis tool

## Features

- List all URLs referenced in a site's `sitemap.xml` file.
- Bootstrap a site's cache.
- Report on page performance metrics using the browser's builtin metrics on `window.performance`

## Installation

### Setup web driver

- Install Firefox
- Install web driver
    ```sh
    brew install geckodriver
    ```

### Setup virtual environment 

- Install Python
    ```sh 
    brew install python@3

    sudo apt-get update && sudo apt-install python3
    ```
- Clone the repo.
- Create a virtual environment in the repo.
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```
- Install production dependencies
    ```sh
    pip install -r requirements.txt
    ```
- Or install prod and dev dependencies at once
    ```sh
    pip install requirements-dev.txt
    ```

### Configuration

- Make a local config.
    ```sh
    cp config_local_template.py config_local.py
    ```
- Set your parameters.

## Usage

Run commands inside the virtual environment.

For help, execute:

```sh
./crawl_site.py -h
```

## Metrics

![Timing overview](https://www.w3.org/TR/navigation-timing/timing-overview.png)

|  Measure (s) | Attribute | Attribute | Summary |
| ------------- | ------------- | ------------- | ------------- |
| Total | loadEventStart | navigationStart | The time taken for the page to load, from clicking on the link until fully loaded in the browser. |
| Data transfer | responseEnd | responseStart | The time taken to download the page, from first byte received, to last. |
| Latency | responseStart | fetchStart | How long it takes the response to get to to the browser. This includes the time it takes for the request to get to the server, the time it takes the server to render a response, and the time until the first byte of that response gets back to the browser. |
| Redirection | redirectEnd | redirectStart | Overhead that is added by HTTP redirects. |
| White Screen | responseStart | navigationStart |  |
| DOM Rendering | domComplete | domLoading |  |
| Request | responseEnd | requestStart |  |
| DOM Interactive | domComplete | domInteractive |  |

## Resources

- [Window.performance - Web APIs](https://developer.mozilla.org/en-US/docs/Web/API/Window/performance) in Mozilla dev docs.
- [Navigation Timing](https://www.w3.org/TR/navigation-timing)

## License

Released under [MIT](/LICENSE).
