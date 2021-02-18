"""URL Management."""

import tldextract

class UrlManagement:
    """Manage URL processing."""

    # Resource reference CSV output columns.
    RESOURCE_REFERENCES_COLUMNS = ['url', 'type', 'cnt']

    # Resource reference CSV output columns.
    EXTERNAL_PAGES_COLUMNS = ['url', 'cnt']

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

        # Domain name to collect from - everything else is ignored.
        self._domain_name = None

    @staticmethod
    def _prep_url(url):
        """Normalise URL."""

        if url:
            url = url.lower().strip()
            if url.endswith('/'):
                url = url[:-1]

            url = url.partition('?')[0]
            url = url.partition('#')[0]

        return url


    def set_domain_name(self, domain_name):
        "Set the domain name to filter on."
        self._domain_name = self._prep_url(domain_name)


    def unprocessed_pages(self, urls=None, action='add'):
        """Manage accessign and processing of URLs for pages to be processed."""
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
                            return True
                    else:
                        self._un_processed_pages_list.append(page_url)
                else:
                    self.external_pages(page_url)

            return False

        return list(self._un_processed_pages_list)


    def processed_pages(self, url=None):
        """Manage accessing and processing of URLs for pages processed."""
        if url:
            page_url = self._prep_url(url)

            self.unprocessed_pages(page_url, 'delete')

            if page_url in self._processed_pages_list:
                return True

            self._processed_pages_list.append(page_url)

            return False

        return list(self._processed_pages_list)


    def processed_resource_references(self, url=None, resource_type=None):
        """
        Manage access to 'resource_references_list' variable.

        Object structure:
        {
            'url': '',
            'type': '',
            'cnt': 0
        }
        """
        if url and resource_type:
            resource_url = self._prep_url(url)
            resource = [resource for resource in self._resource_references_list if resource['url'] == resource_url]

            if resource:
                resource[0]['cnt'] = resource[0]['cnt'] + 1
                return True

            self._resource_references_list.append(
                {
                    'url': resource_url,
                    'type': resource_type,
                    'cnt': 1
                }
            )

            return False

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
                return True

            self._external_pages_list.append(
                {
                    'url': resource_url,
                    'cnt': 1
                }
            )

            return False

        return list(self._external_pages_list)


    def unreachable_pages_list(self, url=None, status_code=None):
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
                return True

            self._unreachable_pages_list.append(
                {
                    'url': resource_url,
                    'status_code': status_code,
                    'cnt': 1
                }
            )

            return False

        return list(self._unreachable_pages_list)
