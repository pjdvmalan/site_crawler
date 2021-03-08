"""
Class to manage Google PageSpeed Insights.
"""
import datetime
import json
import logging
import os
import time
from urllib.parse import urlparse
import requests
import tldextract

from etc import config


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

GOOGLE_PS_API_URL = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'

# Minimum time between calls to Google Insights API.
GOOGLE_PS_API_WAIT_S = 5


class GoogleInsights:
    """Manage requests to Google Page Speed Insights."""


    def __init__(self):
        self.last_processed = int(time.time())


    @staticmethod
    def _dump_json(url, res):
        """Write JSON object to file"""
        domain = tldextract.extract(url).domain
        dir_path = 'var/{}/debug/{}/'.format(domain, datetime.datetime.now().strftime('%Y-%m-%d'))
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        url_path = urlparse(url).path
        url_path = url_path if url_path else '_no_path'
        url_path = url_path.replace('/', '_')

        file_name = '{}{}_{}_insights.json'.format(dir_path, url_path[1:], datetime.datetime.now().strftime('%H-%M'))
        file = open(file_name, "w")
        json.dump(res, file, indent=4)


    def page_performance(self, url, debug=False):
        """Call Google Page Speed Insights API"""
        # https://developers.google.com/speed/docs/insights/v5/reference/pagespeedapi/runpagespeed

        run_time_diff = int(time.time()) - self.last_processed
        if run_time_diff < GOOGLE_PS_API_WAIT_S:
            logging.error('Google Insights API: Waiting until call time reached: %s.', run_time_diff)
            time.sleep(GOOGLE_PS_API_WAIT_S - run_time_diff)

        self.last_processed = int(time.time())

        q_params = { 'url': url,
            'key': config.GOOGLE_PS_API_KEY,
            'strategy': 'DESKTOP', # 'DESKTOP', # MOBILE
            'category': ['PERFORMANCE','ACCESSIBILITY','BEST_PRACTICES','SEO'],
            'locale': 'en'
            }

        res = requests.get(GOOGLE_PS_API_URL, params = q_params)
        if res.status_code==200:
            res = json.loads(res.text)

            if debug:
                self._dump_json(url, res)

        elif res.status_code==429:
            logging.error('Google Insights API: Call limit reached.')

        else:
            logging.error('Google Insights API: Could not process request, URL: %s', url)
            logging.error('Google Insights API: Could not process request, code: %s', res.status_code)
            res = None

        return res
