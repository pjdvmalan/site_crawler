"""
Initialization file for library module.
"""
import argparse
import datetime
import logging
from urllib.parse import urlparse

import requests
from usp.tree import sitemap_tree_for_homepage as site_map_tree
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from etc import config
from .url_management import UrlManagement
from .google_insights import GoogleInsights

# usp.tree logging cannot be disabled in the standard way.
logging.disable(logging.INFO)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

google_insights = GoogleInsights()
url_mgmt = UrlManagement()

MILLISECONDS = 1000.0

BYTE_TO_KILOBYTE = 1024.0

HEADLESS = True

WAIT_S = 20

JS_PAGE_METRICS = """\
    return {
        pageTiming: window.performance.timing,
        resource: window.performance.getEntriesByType("resource")
    }
"""

INITIATORTYPES = ['img', 'script', 'css', 'xhrt', 'font', 'fetch']

RESOURCE_FONTS = ['otf', 'ttf', 'eot', 'woff', 'woff2']

RESOURCE_IMAGES = ['.apng', '.avif', '.gif', '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.png', '.svg', '.webp',
                   '.bmp', '.ico', '.cur', '.tif', '.tiff']

COLUMNS_ANALYSIS = [
    'time', 'url', 'performance', 'accessibility', 'best_practices', 'seo', 'first_contentful_paint',
    'first_contentful_paint_score', 'speed_index', 'speed_index_score', 'largest_contentful_paint',
    'largest_contentful_paint_score', 'interactive', 'interactive_score', 'total_blocking_time',
    'total_blocking_time_score', 'cumulative_layout_shift', 'cumulative_layout_shift_score', 'third_party_wasted',
    'third_party_wasted_size', 'grouping', 'server', 'browser', 'usable', 'total', 'data_transfer', 'redirected', 'dom',
    'img', 'img_sec', 'img_size', 'css', 'css_sec', 'css_size', 'script', 'script_sec', 'script_size', 'font',
    'font_sec', 'font_size', 'xhrt', 'xhrt_sec', 'xhrt_size'
]


def fmt(m_val):
    """Format metric values based on type."""
    if isinstance(m_val,float):
        return float('{:.2f}'.format(m_val))

    return m_val


def process_args():
    """Process arguments from the CLI."""
    parser = argparse.ArgumentParser('Process website URLs referenced in sitemap.xml')
    parser.add_argument('-u', '--url', help='Process single URL.')
    parser.add_argument('-s', '--siteurl', help='Process specified website.')
    parser.add_argument('-m', '--max', type=int, default=0, help='Max number of URLs.')

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


def process_page_metrics(timing_metrics, insights_metrics):
    """Report on page statiscics."""

    p_data = {
        # Lighthouse performance.
        'performance': 0,
        'accessibility': 0,
        'best_practices': 0,
        'seo': 0,
        'first_contentful_paint': 0,
        'first_contentful_paint_score': 0,
        'speed_index': 0,
        'speed_index_score': 0,
        'largest_contentful_paint': 0,
        'largest_contentful_paint_score': 0,
        'interactive': 0,
        'interactive_score': 0,
        'total_blocking_time': 0,
        'total_blocking_time_score': 0,
        'cumulative_layout_shift': 0,
        'cumulative_layout_shift_score': 0,
        'third_party_wasted': 0,
        'third_party_wasted_size': 0,

        # Browser Timing API.
        'server': 0,
        'browser': 0,
        'usable': 0,
        'total': 0,
        'data_transfer': 0,
        'redirected': 0,
        'dom': 0,

        # Artefacts.
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

    # General
    if insights_metrics:
        i_categories = insights_metrics["lighthouseResult"]["categories"]
        p_data['performance'] = fmt(i_categories["performance"]["score"] * 100)
        p_data['accessibility'] = fmt(i_categories["accessibility"]["score"] * 100)
        p_data['best_practices'] = fmt(i_categories["best-practices"]["score"] * 100)
        p_data['seo'] = fmt(i_categories["seo"]["score"] * 100)

        i_audits = insights_metrics["lighthouseResult"]["audits"]
        # Performance
        # firstContentfulPaint : First Contentful Paint (FCP) marks the time at which the first text or image is
        # painted.
        p_data['first_contentful_paint'] = fmt(i_audits["first-contentful-paint"]["numericValue"] / MILLISECONDS)
        p_data['first_contentful_paint_score'] = fmt(i_audits["first-contentful-paint"]["score"]*100)

        # speedIndex : Speed Index shows how quickly the contents of a page are visibly populated.
        p_data['speed_index'] = fmt(i_audits["speed-index"]["numericValue"] / MILLISECONDS)
        p_data['speed_index_score'] = fmt(i_audits["speed-index"]["score"]*100)

        # firstMeaningfulPaint : First Meaningful Paint measures when the primary content of a page is visible.
        p_data['largest_contentful_paint'] = fmt(i_audits["largest-contentful-paint"]["numericValue"] / MILLISECONDS)
        p_data['largest_contentful_paint_score'] = fmt(i_audits["largest-contentful-paint"]["score"]*100)

        # interactive : Time to interactive is the amount of time it takes for the page to become fully interactive.
        p_data['interactive'] = fmt(i_audits["interactive"]["numericValue"] / MILLISECONDS)
        p_data['interactive_score'] = fmt(i_audits["interactive"]["score"]*100)

        # totalBlockingTime : Sum of all time periods between FCP and Time to Interactive, when task length exceeded
        # 50ms, expressed in milliseconds.
        p_data['total_blocking_time'] = fmt(i_audits["total-blocking-time"]["numericValue"] / MILLISECONDS)
        p_data['total_blocking_time_score'] = fmt(i_audits["total-blocking-time"]["score"]*100)

        # cumulativeLayoutShift : new in LightHouse 6, "Cumulative Layout Shift (CLS)" measures the visual stability
        # and quantifies how much a page’s content visually shifts around.
        # Note: Already normalised to seconds.
        p_data['cumulative_layout_shift'] = fmt(i_audits["cumulative-layout-shift"]["numericValue"])
        p_data['cumulative_layout_shift_score'] = fmt(i_audits["cumulative-layout-shift"]["score"]*100)

        # Third party blocking calls.
        third_party = i_audits["third-party-summary"]["details"]["summary"]
        p_data['third_party_wasted'] = fmt(third_party["wastedMs"] / MILLISECONDS)
        p_data['third_party_wasted_size'] = fmt(third_party["wastedBytes"] / BYTE_TO_KILOBYTE)

    # Page Timing Metrics
    if timing_metrics:
        page_timing = timing_metrics['pageTiming']

        p_data['server'] = fmt((page_timing['responseStart'] - page_timing['navigationStart']) / MILLISECONDS)
        p_data['browser'] = fmt((page_timing['domComplete'] - page_timing['responseStart']) / MILLISECONDS)
        p_data['usable'] = fmt((page_timing['domInteractive'] - page_timing['navigationStart']) / MILLISECONDS)
        p_data['total'] = fmt((page_timing['domComplete'] - page_timing['navigationStart']) / MILLISECONDS)
        p_data['data_transfer'] = fmt((page_timing['responseEnd'] - page_timing['responseStart']) / MILLISECONDS)
        p_data['redirected'] = fmt((page_timing['redirectEnd'] - page_timing['redirectStart']) / MILLISECONDS)
        p_data['dom'] = fmt((page_timing['domComplete'] - page_timing['domLoading']) / MILLISECONDS)

        # PerformanceEntry Types: https://developer.mozilla.org/en-US/docs/Web/API/PerformanceEntry/entryType
        # Using the Resource Timing API:
        # https://developer.mozilla.org/en-US/docs/Web/API/Resource_Timing_API/Using_the_Resource_Timing_API

        # PerformanceResourceTiming: https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming
        resources = timing_metrics['resource']
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

            p_data[i_type] = p_data[i_type] + 1
            p_data[i_type + '_sec'] = fmt(p_data[i_type + '_sec'] + (resource['duration'] / MILLISECONDS))
            p_data[i_type + '_size'] = fmt(p_data[i_type + '_size'] + (resource['encodedBodySize'] / BYTE_TO_KILOBYTE))

            url_mgmt.processed_resource_references(resource['name'], i_type)

    return p_data


def process_url(browser, url):
    """Process a single URL."""
    logging.info('Processing: %s', url)

    request = requests.get(url)

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

    timing_api_metrics = browser.execute_script(JS_PAGE_METRICS)
    google_insights_metrics = google_insights.page_performance(url)

    url_mgmt.processed_pages(url)

    links_referenced = browser.find_elements_by_tag_name('a')
    links = [link.get_attribute('href') for link in links_referenced if link.get_attribute('href')]
    url_mgmt.unprocessed_pages(links)

    return {
        'time': format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        'url': url_path,
        'grouping': grouping,
        **process_page_metrics(timing_api_metrics, google_insights_metrics)
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
