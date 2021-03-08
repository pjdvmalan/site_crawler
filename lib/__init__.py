"""
Initialization file for library module.
"""
import argparse
import datetime
import logging
from shutil import rmtree
from urllib.parse import urlparse
import os

import requests
from usp.tree import sitemap_tree_for_homepage as site_map_tree
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from etc import config
from .url_management import UrlManagement
from .google_insights import GoogleInsights
from .metrics import process_page_metrics


# usp.tree logging cannot be disabled in the standard way.
logging.disable(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

google_insights = GoogleInsights()
url_mgmt = UrlManagement()

HEADLESS = True

WAIT_S = 20

JS_PAGE_METRICS = """\
    return {
        pageTiming: window.performance.timing,
        resource: window.performance.getEntriesByType("resource")
    }
"""

COLUMNS_ANALYSIS = [
    'time', 'url', 'performance', 'accessibility', 'best_practices', 'seo', 'first_contentful_paint',
    'first_contentful_paint_score', 'speed_index', 'speed_index_score', 'largest_contentful_paint',
    'largest_contentful_paint_score', 'interactive', 'interactive_score', 'total_blocking_time',
    'total_blocking_time_score', 'cumulative_layout_shift', 'cumulative_layout_shift_score', 'first_input_delay',
    'first_input_delay_score', 'third_party_wasted',
    'third_party_wasted_size', 'grouping', 'server', 'browser', 'usable', 'total', 'data_transfer', 'redirected', 'dom',
    'img', 'img_sec', 'img_size', 'css', 'css_sec', 'css_size', 'script', 'script_sec', 'script_size', 'font',
    'font_sec', 'font_size', 'xhrt', 'xhrt_sec', 'xhrt_size'
]


def delete_reports():
    """Delete all reports."""
    report_directory = 'var/'
    for files in os.listdir(report_directory):
        path = os.path.join(report_directory, files)
        if path == 'var/.gitkeep':
            continue
        try:
            rmtree(path)
        except OSError:
            os.remove(path)


def process_args():
    """Process arguments from the CLI."""
    parser = argparse.ArgumentParser('Process website URLs referenced in sitemap.xml')
    parser.add_argument('-u', '--url', help='Process single URL.')
    parser.add_argument('-s', '--siteurl', help='Process specified website.')
    parser.add_argument('-m', '--max', type=int, default=0, help='Max number of URLs to process.')
    parser.add_argument('-f', '--follow', action='store_true', help='Follow internal URLs.')
    parser.add_argument('-d', '--debug', action='store_true', help='Enable debug output.')
    parser.add_argument('-rr', '--remove_reports', action='store_true', help='Remove all reports.')

    return parser.parse_args()


def conf_browser():
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


def process_url(browser, url, follow_links, debug=False):
    """Process a single URL."""
    logging.info('Processing: %s', url)

    try:
        request = requests.get(url)
    except requests.RequestException as ex:
        url_mgmt.unreachable_pages(url, ex)
        logging.error('Error loading: %s - status: %s', url, ex)
        return {}

    if request.status_code != 200:
        url_mgmt.unreachable_pages(url, request.status_code)
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
    url_path = url_path if url_path else 'root'

    timing_api_metrics = browser.execute_script(JS_PAGE_METRICS)
    google_insights_metrics = google_insights.page_performance(url, debug)

    url_mgmt.processed_pages(url)

    if follow_links:
        links_referenced = browser.find_elements_by_tag_name('a')
        links = [link.get_attribute('href') for link in links_referenced if link.get_attribute('href')]
        url_mgmt.unprocessed_pages(links)

    return {
        'time': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'url': url_path,
        'grouping': grouping,
        **process_page_metrics(url_path, timing_api_metrics, google_insights_metrics, url_mgmt)
    }


def process_sitemap(site_url, max_urls):
    """Iterate through and process all pages in a website's sitemap."""
    counter = 0

    target_url = site_url if site_url else config.TARGER_URL
    site_map = site_map_tree(target_url)
    res = []

    for page in site_map.all_pages():
        page_url = page.url.lower()
        if page_url in url_mgmt.processed_pages() or page_url in config.EXCLUDE_PATHS:
            continue

        # max_urls apply only to non duplicate/excluded URLs.
        if max_urls:
            counter += 1
            if counter > max_urls:
                break

        res.append(page_url)

    return res


def report_results(results):
    """Process the result data."""
    url_mgmt.analysis_report(COLUMNS_ANALYSIS, results)
    url_mgmt.generate_report('analysis', COLUMNS_ANALYSIS, results)
    url_mgmt.generate_internal_reports()
