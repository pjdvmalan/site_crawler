#!/usr/bin/env python
"""
Site crawler application.
"""

import traceback
import tldextract
from etc import config
from lib import report_results, conf_browser, logging, process_args, process_url, process_sitemap, url_mgmt
from lib import delete_reports


def main():
    """
    Command-line entrypoint to process a URL or sitemap and show a report if needed.
    """

    browser = None
    results = []
    args = process_args()

    try:
        if args.remove_reports:
            delete_reports()
            return

        source_url_path = args.url if args.url else args.siteurl if args.siteurl else config.TARGER_URL
        if not source_url_path:
            logging.error('No URLs to analyse.')
            return

        domain_name = tldextract.extract(source_url_path).domain
        url_mgmt.set_domain_name(domain_name)

        browser = conf_browser()

        if args.url:
            url_mgmt.unprocessed_pages(args.url)

        else:
            url_mgmt.unprocessed_pages(process_sitemap(args.siteurl, args.max))

        proc_cnt = 0
        while True:
            if url_mgmt.unprocessed_pages(clone=False):
                if args.max:
                    if proc_cnt == args.max:
                        break

                proc_cnt += 1
                total = len(url_mgmt.unprocessed_pages(clone=False)) + proc_cnt

                page = url_mgmt.unprocessed_pages(clone=False)[0]
                page_results = process_url(browser, page, args.follow, args.debug)
                if page_results:
                    results.append(page_results)

                print('Processed: {}/{}'.format(proc_cnt, total))

            else:
                break

        report_results(results)

    except Exception as ex:
        logging.error('Exception: %s', ex)
        traceback.print_exc()

    finally:
        if browser:
            browser.quit()


if __name__ == '__main__':
    main()
