"""
Initliazation file for library module.
"""

import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.common.exceptions import TimeoutException
import argparse
import pandas as pd
from etc import config

# usp.tree logging cannot be disabled in the standard way.
import logging
logging.disable(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

MILLISECONDS = 1000.0

pd.set_option('display.precision', 2)


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
    ff_options.headless = True
    browser = webdriver.Firefox(options=ff_options)
    browser.implicitly_wait(20)
    return browser


def process_url(browser, url):
    logging.info('Processing: %s', url)
    request = requests.get(url)
    if request.status_code != 200:
        logging.error('Error loading: %s - status: %s', url, request.status_code)

    else:
        try:
            browser.get(url)
        except TimeoutException:
            logging.error('TimeoutException: Error loading: %s', url)

        except requests.exceptions.RequestException:
            logging.error('RequestException: Error loading: %s', url)
        except Exception:
            logging.error('Exception: Error loading: %s', url)

        grouping = 'Not categorised'
        for key, value in config.df_group_by.items():
            if value in url:
                grouping = key

        timings = browser.execute_script('var performance = window.performance || {};' +
                                         'var timings = performance.timing || {}; return timings;')

        total = (timings['loadEventEnd'] - timings['navigationStart']) / MILLISECONDS
        data_transfer = (timings['responseEnd'] - timings['responseStart']) / MILLISECONDS
        latency = (timings['responseStart'] - timings['fetchStart']) / MILLISECONDS
        redirection = (timings['redirectEnd'] - timings['redirectStart']) / MILLISECONDS
        white_screen = (timings['responseStart'] - timings['navigationStart']) / MILLISECONDS
        dom_rendering = (timings['domComplete'] - timings['domLoading']) / MILLISECONDS
        request_span = (timings['responseEnd'] - timings['requestStart']) / MILLISECONDS
        dom_interactive = (timings['domComplete'] - timings['domInteractive']) / MILLISECONDS

        url_path = url[len(config.target_url):]
        return {'url': url_path, 'Grouping': grouping,
                'total': total,
                'data_transfer': data_transfer,
                'latency': latency,
                'redirection': redirection,
                'white_screen': white_screen,
                'dom_rendering': dom_rendering,
                'request': request_span,
                'dom_interactive': dom_interactive
                }


def analysis_report(data):
    df = pd.DataFrame(data, columns=['url', 'Grouping',
                                     'total', 'data_transfer', 'latency', 'redirection',
                                     'white_screen', 'dom_rendering', 'request',
                                     'dom_interactive'])
    print('\nSummary:')
    print(df.describe())
    print('\n--------------------------------------')
    print('Mean:')
    print(df.groupby('Grouping', as_index=False)[['total_time']].mean())
    print('\n--------------------------------------')
    print('Max:')
    print(df.groupby('Grouping', as_index=False)[['total_time']].max())
    print('\nWorst performing pages reported in: analysis_report.csv\n')
    df.nlargest(15, 'total_time').to_csv('analysis_report.csv')
