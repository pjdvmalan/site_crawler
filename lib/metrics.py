"""
Metrics related processing.
"""

MILLISECONDS = 1000.0

BYTE_TO_KILOBYTE = 1024.0

INITIATORTYPES = ['img', 'script', 'css', 'xhrt', 'font', 'fetch']

RESOURCE_FONTS = ['otf', 'ttf', 'eot', 'woff', 'woff2']

RESOURCE_IMAGES = ['.apng', '.avif', '.gif', '.jpg', '.jpeg', '.jfif', '.pjpeg', '.pjp', '.png', '.svg', '.webp',
                   '.bmp', '.ico', '.cur', '.tif', '.tiff']


def fmt(m_val):
    """Format metric values based on type."""
    if isinstance(m_val,float):
        return float('{:.2f}'.format(m_val))

    return m_val


def process_insights_metrics(insights_metrics):
    """Create a dictionary with the insights metrics"""
    metrics = {}

    i_categories = insights_metrics["lighthouseResult"]["categories"]
    metrics['performance'] = fmt(i_categories["performance"]["score"] * 100)
    metrics['accessibility'] = fmt(i_categories["accessibility"]["score"] * 100)
    metrics['best_practices'] = fmt(i_categories["best-practices"]["score"] * 100)
    metrics['seo'] = fmt(i_categories["seo"]["score"] * 100)

    i_audits = insights_metrics["lighthouseResult"]["audits"]
    metrics['first_contentful_paint'] = fmt(i_audits["first-contentful-paint"]["numericValue"] / MILLISECONDS)
    metrics['first_contentful_paint_score'] = fmt(i_audits["first-contentful-paint"]["score"]*100)
    metrics['speed_index'] = fmt(i_audits["speed-index"]["numericValue"] / MILLISECONDS)
    metrics['speed_index_score'] = fmt(i_audits["speed-index"]["score"]*100)
    metrics['largest_contentful_paint'] = fmt(i_audits["largest-contentful-paint"]["numericValue"] / MILLISECONDS)
    metrics['largest_contentful_paint_score'] = fmt(i_audits["largest-contentful-paint"]["score"]*100)
    metrics['interactive'] = fmt(i_audits["interactive"]["numericValue"] / MILLISECONDS)
    metrics['interactive_score'] = fmt(i_audits["interactive"]["score"]*100)
    metrics['total_blocking_time'] = fmt(i_audits["total-blocking-time"]["numericValue"] / MILLISECONDS)
    metrics['total_blocking_time_score'] = fmt(i_audits["total-blocking-time"]["score"]*100)
    # Note: Already normalised to seconds.
    metrics['cumulative_layout_shift'] = fmt(i_audits["cumulative-layout-shift"]["numericValue"])
    metrics['cumulative_layout_shift_score'] = fmt(i_audits["cumulative-layout-shift"]["score"]*100)
    # Keep in milliseconds.
    metrics['first_input_delay'] = (i_audits["max-potential-fid"]["numericValue"])
    metrics['first_input_delay_score'] = fmt(i_audits["max-potential-fid"]["score"]*100)
    # Third party blocking calls.
    # third_party = i_audits["third-party-summary"]["details"]["summary"]
    # metrics['third_party_wasted'] = fmt(third_party["wastedMs"] / MILLISECONDS)
    # metrics['third_party_wasted_size'] = fmt(third_party["wastedBytes"] / BYTE_TO_KILOBYTE)

    return metrics


def _process_audit_item(url, audit_item, url_mgmt):
    """Process the identified item."""
    details = audit_item.get('details')
    if details:
        for item in details['items']:
            url_mgmt.audit_results(url, audit_item, item)


def process_audit(url, insights_metrics, url_mgmt):
    """Identify areas of improvement."""
    i_audits = insights_metrics["lighthouseResult"]["audits"]
    for key in i_audits:
        audit_item = i_audits[key]
        if audit_item['scoreDisplayMode'] == 'notApplicable':
            continue

        if audit_item['scoreDisplayMode'] == 'binary' and audit_item['score'] == 0:
            _process_audit_item(url, audit_item, url_mgmt)

        elif audit_item['scoreDisplayMode'] == 'binary' and audit_item['score'] <= 0.8:
            _process_audit_item(url, audit_item, url_mgmt)

        elif audit_item['scoreDisplayMode'] == 'numeric' and audit_item['score'] <= 0.8:
            _process_audit_item(url, audit_item, url_mgmt)

        # elif audit_item['scoreDisplayMode'] == 'binary' and audit_item['score'] <= 0.8:
        #     _process_audit_item(url, audit_item, url_mgmt)
        # elif key == 'render-blocking-resources' and audit_item['score'] < 0.8:
        #     _process_audit_item(url, audit_item, url_mgmt)


def process_timing_metrics(timing_metrics):
    """Create a dictionary with the timing metrics to a dictionary."""
    metrics = {}

    page_timing = timing_metrics['pageTiming']

    metrics['server'] = fmt((page_timing['responseStart'] - page_timing['navigationStart']) / MILLISECONDS)
    metrics['browser'] = fmt((page_timing['domComplete'] - page_timing['responseStart']) / MILLISECONDS)
    metrics['usable'] = fmt((page_timing['domInteractive'] - page_timing['navigationStart']) / MILLISECONDS)
    metrics['total'] = fmt((page_timing['domComplete'] - page_timing['navigationStart']) / MILLISECONDS)
    metrics['data_transfer'] = fmt((page_timing['responseEnd'] - page_timing['responseStart']) / MILLISECONDS)
    metrics['redirected'] = fmt((page_timing['redirectEnd'] - page_timing['redirectStart']) / MILLISECONDS)
    metrics['dom'] = fmt((page_timing['domComplete'] - page_timing['domLoading']) / MILLISECONDS)

    return metrics


def process_page_resources(source_url, timing_metrics, url_mgmt):
    """Create a dictionary with resource usage."""
    metrics = {
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
        'other_size': 0
    }

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

        metrics[i_type] = metrics[i_type] + 1
        metrics[i_type + '_sec'] = fmt(metrics[i_type + '_sec'] + (resource['duration'] / MILLISECONDS))
        metrics[i_type + '_size'] = fmt(metrics[i_type + '_size'] + (resource['encodedBodySize'] / BYTE_TO_KILOBYTE))

        url_mgmt.processed_resource_references(source_url, resource['name'], i_type)

    return metrics


def process_page_metrics(source_url, timing_metrics, insights_metrics, url_mgmt):
    """Report on page statistics."""

    metrics = {}

    # Google Page Speed Insights.
    if insights_metrics:
        metrics = process_insights_metrics(insights_metrics)
        process_audit(source_url, insights_metrics, url_mgmt)

    # Page Timing Metrics.
    if timing_metrics:
        metrics.update(process_timing_metrics(timing_metrics))
        metrics.update(process_page_resources(source_url, timing_metrics, url_mgmt))

    return metrics
