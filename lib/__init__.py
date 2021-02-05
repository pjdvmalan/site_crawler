"""
Initialization file for library module.
"""
import argparse
from csv import DictWriter
import datetime
import logging
import os
from urllib.parse import urlparse

import pandas as pd
import requests
from usp.tree import sitemap_tree_for_homepage as site_map_tree
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import sidetable
import tldextract

from etc import config

# usp.tree logging cannot be disabled in the standard way.
logging.disable(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
pd.set_option('display.precision', 2)


MILLISECONDS = 1000.0

BYTE_TO_KILOBYTE = 1024.0

HEADLESS = True

WAIT_S = 20

JS_PAGE_METRICS = """\
    return {
        pageTiming: window.performance.timing,
        navigation: window.performance.getEntriesByType("navigation"),
        resource: window.performance.getEntriesByType("resource"),
        paint: window.performance.getEntriesByType("paint")
    }
"""

INITIATORTYPES = ['img', 'script', 'css', 'xhrt', 'font', 'fetch']

RESOURCE_FONTS = ['otf', 'ttf', 'eot', 'woff', 'woff2']

RESOURCE_IMAGES = ['.apng', '.avif', '.gif', '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.png', '.svg', '.webp',
                   '.bmp', '.ico', '.cur', '.tif', '.tiff']

COLUMNS = [
    'time', 'url', 'grouping', 'server', 'browser', 'usable', 'total', 'data_transfer', 'redirected', 'dom', 'fcp',
    'img', 'img_sec', 'img_size', 'css', 'css_sec', 'css_size', 'script', 'script_sec', 'script_size', 'font',
    'font_sec', 'font_size', 'xhrt', 'xhrt_sec', 'xhrt_size'
]

# List of URLs processed.
PROCESSED_PAGES = []

# List of URLs to be checked.
UN_PROCESSED_PAGES = []

# List of resources referenced.
RESOURCE_REFERENCES = []

# Resource reference CSV output columns.
RESOURCE_REFERENCES_COLUMNS = ['url', 'type', 'cnt']


def processed_pages(url):
    """Manage access to PROCESSED_PAGES global variable."""
    if url:
        page_url = url.lower().strip()
        if page_url in PROCESSED_PAGES:
            return True

        PROCESSED_PAGES.append(page_url)
        return False

    return PROCESSED_PAGES


def processed_resource_references(url, resource_type):
    """
    Manage access to PROCESSED_PAGES global variable.

    Object structure:
    {
        'url': '',
        'type': '',
        'cnt': 0
    }
    """
    if url and resource_type:
        resource_url = url.lower().strip()
        resource = [resource for resource in RESOURCE_REFERENCES if resource['url'] == resource_url]

        if resource:
            resource[0]['cnt'] = resource[0]['cnt'] + 1
            return True

        RESOURCE_REFERENCES.append(
            {
                'url': resource_url,
                'type': resource_type,
                'cnt': 1
            }
        )
        return False

    return RESOURCE_REFERENCES


def process_arguments():
    """Process arguments from the CLI."""
    parser = argparse.ArgumentParser('Process website URLs referenced in sitemap.xml')

    parser.add_argument('-l', '--list', action='store_true', help='List URLs referenced in sitemap.xml.')
    parser.add_argument('-a', '--skip_analysis', action='store_true', help='Do not analyse pages.')
    parser.add_argument('-r', '--report', action='store_true', help='Report results.')
    parser.add_argument('-u', '--url', help='Process single URL.')
    parser.add_argument('-s', '--siteurl', help='Process specified website.')
    parser.add_argument('-m', '--max', type=int, default=0, help='Max number of URLs.')

    return parser.parse_args()


def configure_browser():
    """Configure the browser instance."""
    ff_options = FirefoxOptions()
    ff_options.headless = HEADLESS

    browser = webdriver.Firefox(options=ff_options)
    browser.implicitly_wait(WAIT_S)

    return browser


def load(browser, url):
    """Load the page into the browser instance."""
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


def process_page_data(page_metrics):
    """Report on page statiscics."""

    page_info = {
        'server': 0,
        'browser': 0,
        'usable': 0,
        'total': 0,
        'data_transfer': 0,
        'redirected': 0,
        'dom': 0,
        'fcp': 0,

        'img': 0,
        'img_sec': 0,
        'img_size': 0,

        'css': 0,
        'css_sec': 0,
        'css_size': 0,

        'script': 0,
        'script_sec': 0,
        'script_size': 0,

        'font': 0,
        'font_sec': 0,
        'font_size': 0,

        'xhrt': 0,
        'xhrt_sec': 0,
        'xhrt_size': 0,

        'fetch': 0,
        'fetch_sec': 0,
        'fetch_size': 0,

        'other': 0,
        'other_sec': 0,
        'other_size': 0,
    }

    # Window.performance: https://www.w3.org/TR/navigation-timing/#sec-navigation-timing-interface
    page_timing = page_metrics['pageTiming']

    # https://mkaz.blog/code/use-python-selenium-to-automate-web-timing/
    page_info['server'] = (page_timing['responseStart'] - page_timing['navigationStart']) / MILLISECONDS
    page_info['browser'] = (page_timing['domComplete'] - page_timing['responseStart']) / MILLISECONDS
    page_info['usable'] = (page_timing['domInteractive'] - page_timing['navigationStart']) / MILLISECONDS
    page_info['total'] = (page_timing['domComplete'] - page_timing['navigationStart']) / MILLISECONDS
    page_info['data_transfer'] = (page_timing['responseEnd'] - page_timing['responseStart']) / MILLISECONDS
    page_info['redirected'] = (page_timing['redirectEnd'] - page_timing['redirectStart']) / MILLISECONDS
    page_info['dom'] = (page_timing['domComplete'] - page_timing['domLoading']) / MILLISECONDS

    # PerformanceEntry Types: https://developer.mozilla.org/en-US/docs/Web/API/PerformanceEntry/entryType
    # Using the Resource Timing API:
    # https://developer.mozilla.org/en-US/docs/Web/API/Resource_Timing_API/Using_the_Resource_Timing_API

    # PerformanceNavigationTiming: https://developer.mozilla.org/en-US/docs/Web/API/PerformanceNavigationTiming
    # NOTE: page_timing will be depricated and will hve to use the navigation object.
    # navigation = page_metrics['navigation']

    # PerformanceResourceTiming: https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming
    resources = page_metrics['resource']
    for resource in resources:
        i_type = resource['initiatorType'].lower()
        if i_type not in INITIATORTYPES:
            if i_type == 'xmlhttprequest':
                i_type = 'xhrt'

            elif resource['name'].endswith(tuple(RESOURCE_FONTS)):
                i_type = 'font'

            elif resource['name'].endswith(tuple(RESOURCE_IMAGES)):
                i_type = 'img'

            elif resource['name'].endswith('.css'):
                i_type = 'css'

            elif resource['name'].endswith('.js'):
                i_type = 'script'

            else:
                i_type = 'other'

        page_info[i_type] = page_info[i_type] + 1
        page_info[i_type + '_sec'] = page_info[i_type + '_sec'] + (resource['duration'] / MILLISECONDS)
        page_info[i_type + '_size'] = page_info[i_type + '_size'] + (resource['encodedBodySize'] / BYTE_TO_KILOBYTE)

        processed_resource_references(resource['name'], i_type)

    # PerformancePaintTiming: https://developer.mozilla.org/en-US/docs/Web/API/PerformancePaintTiming
    paint = page_metrics['paint']
    if len(paint) == 1 and paint[0]['name'] == 'first-contentful-paint':
        page_info['fcp'] = (paint[0]['startTime']) / MILLISECONDS

    else:
        logging.error('PerformancePaintTiming: Number of results not expected.')

    return page_info


def process_url(browser, url):
    """Process a single URL."""
    logging.info('Processing: %s', url)

    request = requests.get(url)

    if request.status_code != 200:
        logging.error('Error loading: %s - status: %s', url, request.status_code)

        return {}

    loaded_ok = load(browser, url)

    if not loaded_ok:
        return {}

    grouping = 'Not categorised'
    for key, value in config.DF_GROUP_BY.items():
        if value in url:
            grouping = key

    url_path = urlparse(url).path

    page_metrics = browser.execute_script(JS_PAGE_METRICS)

    return {
        'time': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'url': url_path,
        'grouping': grouping,
        **process_page_data(page_metrics)
    }


def process_sitemap(browser, site_url, max_urls, show_list, skip_analysis, exclude_urls):
    """Iterate through and process all pages in a website's sitemap."""
    results = []

    counter = 0

    target_url = site_url if site_url else config.TARGER_URL
    site_map = site_map_tree(target_url)

    for page in site_map.all_pages():
        page_url = page.url.lower()
        if page_url in processed_pages(None) or page_url in exclude_urls:
            continue

        # max_urls apply only to non duplicate/excluded URLs.
        if max_urls:
            counter += 1
            if counter > max_urls:
                break

        processed_pages(page_url)

        if show_list:
            print(page_url)
        if not skip_analysis:
            results.append(process_url(browser, page_url))

    return results


def write_report_output(source_url_path, data_frame):
    """Write the output of the results to file."""
    domain_name = tldextract.extract(source_url_path).domain
    dir_path = 'var/{}/'.format(domain_name)
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)

    # Output main results.
    file_name = 'analysis_report_{}.csv'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
    full_path = '{}{}'.format(dir_path, file_name)

    data_frame.to_csv(path_or_buf=full_path, index=False)
    print('\nReport: {}'.format(full_path))

    # Output resource references.
    file_name = 'resource_references_report_{}.csv'.format(datetime.datetime.now().strftime('%Y-%m-%d_%H_%M_%S'))
    full_path = '{}{}'.format(dir_path, file_name)

    with open(full_path, 'w') as outfile:
        writer = DictWriter(outfile, fieldnames=RESOURCE_REFERENCES_COLUMNS)
        writer.writeheader()
        writer.writerows(processed_resource_references(None, None))

    print('Report: {}\n'.format(full_path))


def analysis_report(data_frame):
    """Print a summary of the report to the console."""
    print('\nSummary:')
    print(data_frame.describe())
    print('\n--------------------------------------')

    total_grouping = data_frame.groupby('grouping', as_index=True)[['total']]
    print('Max:')
    print(total_grouping.max())
    print('--------------------------------------')

    print('Mean:')
    print(total_grouping.mean())
    print('\n--------------------------------------')

    print('Category distribution:')
    print(data_frame.stb.freq(['grouping']))


def report_results(source_url_path, results):
    "Process the result data."
    data_frame = pd.DataFrame(results, columns=COLUMNS)

    analysis_report(data_frame)
    write_report_output(source_url_path, data_frame)
