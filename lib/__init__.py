"""
Initialization file for library module.
"""
import argparse
import logging

import pandas as pd
import requests
import sidetable
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from etc import config

# usp.tree logging cannot be disabled in the standard way.
logging.disable(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
pd.set_option('display.precision', 2)


MILLISECONDS = 1000.0

HEADLESS = True
WAIT_S = 20

JS_SCRIPT = """\
var performance = window.performance || {};
var timings = performance.timing || {};
return timings;
"""

COLUMNS = [
    'url', 'Grouping', 'total', 'data_transfer', 'latency', 'redirection', 'white_screen', 'dom_rendering', 'request',
    'dom_interactive'
]


def process_arguments():
    parser = argparse.ArgumentParser('Process website URLs referenced in sitemap.xml')

    parser.add_argument('-l', '--list', action='store_true', help='List URLs referenced in sitemap.xml.')
    parser.add_argument('-r', '--report', action='store_true', help='Report results.')
    parser.add_argument('-u', '--url', help='Process single URL.')
    parser.add_argument('-s', '--siteurl', help='Process specified website.')
    parser.add_argument('-m', '--max', type=int, default=0, help='Max number of URLs.')

    return parser.parse_args()


def configure_browser():
    ff_options = FirefoxOptions()
    ff_options.headless = HEADLESS

    browser = webdriver.Firefox(options=ff_options)
    browser.implicitly_wait(WAIT_S)

    return browser


def load(browser, url):
    loaded_ok = False

    try:
        browser.get(url)
    except TimeoutException:
        logging.error('TimeoutException: Error loading: %s', url)
    except requests.exceptions.RequestException:
        logging.error('RequestException: Error loading: %s', url)
    except Exception:
        logging.error('Exception: Error loading: %s', url)
    else:
        loaded_ok = True

    return loaded_ok


def process_timings(timings):
    total = (timings['loadEventEnd'] - timings['navigationStart'])
    data_transfer = (timings['responseEnd'] - timings['responseStart']) / MILLISECONDS
    latency = (timings['responseStart'] - timings['fetchStart']) / MILLISECONDS
    redirection = (timings['redirectEnd'] - timings['redirectStart']) / MILLISECONDS
    white_screen = (timings['responseStart'] - timings['navigationStart']) / MILLISECONDS
    dom_rendering = (timings['domComplete'] - timings['domLoading']) / MILLISECONDS
    request_span = (timings['responseEnd'] - timings['requestStart']) / MILLISECONDS
    dom_interactive = (timings['domComplete'] - timings['domInteractive']) / MILLISECONDS

    return {
        'total': total,
        'data_transfer': data_transfer,
        'latency': latency,
        'redirection': redirection,
        'white_screen': white_screen,
        'dom_rendering': dom_rendering,
        'request': request_span,
        'dom_interactive': dom_interactive
    }


def process_url(browser, url):
    logging.info('Processing: %s', url)

    request = requests.get(url)

    if request.status_code != 200:
        logging.error('Error loading: %s - status: %s', url, request.status_code)

        return {}

    loaded_ok = load(browser, url)

    if not loaded_ok:
        return {}

    grouping = 'Not categorised'
    for key, value in config.df_group_by.items():
        if value in url:
            grouping = key

    url_path = url[len(config.target_url):]
    timings = browser.execute_script(JS_SCRIPT)

    return {
        'url': url_path,
        'Grouping': grouping,
        **process_timings(timings)
    }


def analysis_report(results):
    df = pd.DataFrame(results, columns=COLUMNS)

    print('\nSummary:')
    print(df.describe())
    print('\n--------------------------------------')

    total_grouping = df.groupby('Grouping', as_index=True)[['total']]
    print('Max:')
    print(total_grouping.max())
    print('--------------------------------------')

    print('Mean:')
    print(total_grouping.mean())
    print('\n--------------------------------------')

    print('Category distribution:')
    print(df.stb.freq(['Grouping']))

    df.nlargest(100, 'total').to_csv('analysis_report.csv')

    print('\nWorst performing pages reported in: analysis_report.csv\n')
