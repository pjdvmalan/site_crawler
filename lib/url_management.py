"""
URL Management.
"""
import datetime
import logging
import os

import pandas as pd
import tldextract

# Sidetable accessed through the new .stb accessor on your DataFrame.
# Adds category distribution capability to 'analysis_report()'.
import sidetable

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

pd.set_option('display.precision', 2)


class UrlManagement:
    """Manage URL processing."""

    # Resource reference CSV output columns.
    COLUMNS_RESOURCE_REFERENCES = ['url', 'type', 'cnt']

    # Resource reference CSV output columns.
    COLUMNS_EXTERNAL_PAGES = ['url', 'cnt']

    COLUMNS_AUDIT_RESULTS = ['url', 'id', 'title', 'finding', 'saving_ms', 'description', 'detail']

    # Basic URL list.
    COLUMNS_BASIC = ['url']


    def __init__(self):
        # List of URLs processed.
        self._processed_pages_list = []

        # List of URLs to be checked.
        self._un_processed_pages_list = []

        # List of resources referenced.
        self._resource_references_list = []

        # List of pages that could not be reached.
        self._unreachable_pages_list = []

        # List of pages referenced outside of domain.
        self._external_pages_list = []

        # List of audit results.
        self._audit_results_list = []

        # Domain name to collect from - everything else is ignored.
        self._domain_name = ''


    @staticmethod
    def _prep_url(url):
        """Normalise URL."""

        if url:
            url = url.partition('?')[0]
            url = url.partition('#')[0]

            url = url.lower().strip()
            if url.endswith('/'):
                url = url[:-1]

        return url


    def set_domain_name(self, domain_name):
        "Set the domain name to filter on."
        self._domain_name = self._prep_url(domain_name)


    def unprocessed_pages(self, urls=None, action='add', clone=True):
        """Manage accessing and processing of URLs for pages to be processed."""
        if urls:
            # Convert a string to a list.
            if isinstance(urls, str):
                urls = [urls]

            for url in urls:
                page_url = self._prep_url(url)
                domain_name = tldextract.extract(page_url).domain

                # Filter out telephone numbers and email addresses.
                if domain_name == '' or '@' in page_url:
                    continue

                if domain_name == self._domain_name:
                    if page_url in self._un_processed_pages_list:
                        if action == 'delete':
                            self._un_processed_pages_list.remove(page_url)
                            return []
                    else:
                        self._un_processed_pages_list.append(page_url)
                else:
                    self.external_pages(page_url)

            return []

        if clone:
            return list(self._un_processed_pages_list)

        return self._un_processed_pages_list


    def processed_pages(self, url=None):
        """Manage accessing and processing of URLs for pages processed."""
        if url:
            page_url = self._prep_url(url)

            self.unprocessed_pages(page_url, 'delete')

            if page_url not in self._processed_pages_list:
                self._processed_pages_list.append(page_url)

            return []

        return list(self._processed_pages_list)


    def processed_resource_references(self, source_url=None, url=None, resource_type=None):
        """
        Manage access to 'resource_references_list' variable.

        Object structure:
        {
            'url': str,
            'type': '',
            'cnt': 0
            'sample_src_url': ''
        }
        """
        if url and resource_type:
            resource_url = self._prep_url(url)
            resource = [resource for resource in self._resource_references_list if resource['url'] == resource_url]

            if resource:
                resource[0]['cnt'] = resource[0]['cnt'] + 1
                return []

            self._resource_references_list.append(
                {
                    'url': resource_url,
                    'type': resource_type,
                    'cnt': 1,
                    'sample_src_url': source_url
                }
            )

            return []

        return list(self._resource_references_list)


    def external_pages(self, url=None):
        """
        Manage access to '_external_pages_list' variable.

        Object structure:
        {
            'url': '',
            'cnt': 0
        }
        """
        if url:
            resource_url = self._prep_url(url)
            resource = [resource for resource in self._external_pages_list if resource['url'] == resource_url]

            if resource:
                resource[0]['cnt'] = resource[0]['cnt'] + 1
                return []

            self._external_pages_list.append(
                {
                    'url': resource_url,
                    'cnt': 1
                }
            )

            return []

        return list(self._external_pages_list)


    def unreachable_pages(self, url=None, status_code=None):
        """
        List of URLs that could not be reached.

        Object structure:
        {
            'url': '',
            'status_code': 0,
            'cnt': 0
        }
        """
        if url and status_code:
            resource_url = self._prep_url(url)
            resource = [resource for resource in self._unreachable_pages_list if resource['url'] == resource_url]

            if resource:
                resource[0]['cnt'] = resource[0]['cnt'] + 1
                return []

            self._unreachable_pages_list.append(
                {
                    'url': resource_url,
                    'status_code': status_code,
                    'cnt': 1
                }
            )

            return []

        return list(self._unreachable_pages_list)


    def audit_results(self, url=None, item=None, detail=None):
        """
        Manage access to '_audit_results_list' variable.
        """

        if url:
            resource_url = self._prep_url(url)

            self._audit_results_list.append(
                {
                    'url': resource_url,
                    'id': item.get('id', 'No ID'),
                    'title': item.get('title', 'No Title'),
                    'finding': item.get('displayValue', ''),
                    'saving_ms': item.get('overallSavingsMs', 0),
                    'description': item['description'],
                    'detail': detail
                }
            )

            return []

        return list(self._audit_results_list)


    @staticmethod
    def analysis_report(columns, values):
        """Print a summary of the report to the console."""

        data_frame = pd.DataFrame(values, columns=columns)

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
        print('')


    def generate_report(self, file_name, columns, values):
        """Output URL lists to CSV."""
        if values:
            if self._domain_name:
                dir_path = 'var/{}/{}/'.format(self._domain_name, datetime.datetime.now().strftime('%Y-%m-%d'))
            else:
                dir_path = 'var/{}/'.format(datetime.datetime.now().strftime('%Y-%m-%d'))

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            file_name = '{}_{}.csv'.format(file_name, datetime.datetime.now().strftime('%H-%M-%S'))
            full_path = '{}{}'.format(dir_path, file_name)

            data_frame = pd.DataFrame(values, columns=columns)
            data_frame.to_csv(path_or_buf=full_path, index=False)

        else:
            logging.warning('Report: %s - nothing to report on.', file_name)


    def generate_internal_reports(self):
        """Write the output of the results to file."""
        self.generate_report('external_uri', self.COLUMNS_EXTERNAL_PAGES, self.external_pages())
        self.generate_report('resource_uri', self.COLUMNS_RESOURCE_REFERENCES, self.processed_resource_references())
        self.generate_report('processed_uri', self.COLUMNS_BASIC, self.processed_pages())
        self.generate_report('unreachable_uri', self.COLUMNS_BASIC, self.unreachable_pages())
        self.generate_report('unprocessed_uri', self.COLUMNS_BASIC, self.unprocessed_pages())
        self.generate_report('audit', self.COLUMNS_AUDIT_RESULTS, self.audit_results())
