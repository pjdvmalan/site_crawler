#!/usr/bin/env python
"""
Site crawler application.
"""
from usp.tree import sitemap_tree_for_homepage as site_map_tree

from lib import process_arguments, configure_browser, analysis_report, logging, process_url
from etc import config


args = process_arguments()
browser = configure_browser()

exclude_urls = config.exclude_paths

processed_urls = []
data = []
idx = 0

try:
    if args.url:
        data.append(process_url(browser, args.url))
    else:
        target_url = args.siteurl if args.siteurl else config.target_url
        site_map = site_map_tree(target_url)
        for page in site_map.all_pages():
            if args.max > 0:
                idx = idx + 1
                if idx > args.max:
                    break

            if page.url not in processed_urls and page.url not in exclude_urls:
                processed_urls.append(page.url)

                if args.list:
                    print(page.url)

                else:
                    data.append(process_url(browser, page.url))

    if args.report:
        analysis_report(data)

except Exception as e:
    logging.error('Exception: Error loading: %s', e)

finally:
    browser.quit()
