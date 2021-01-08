#!/usr/bin/env python
"""
Site crawler application.
"""
from usp.tree import sitemap_tree_for_homepage as site_map_tree

from etc import config
from lib import analysis_report, configure_browser, logging, process_arguments, process_url


def process_sitemap(browser, site_url, max_urls, show_list, show_report, exclude_urls):
    results = []

    counter = 0
    processed_urls = []

    target_url = site_url if site_url else config.target_url
    site_map = site_map_tree(target_url)

    for page in site_map.all_pages():
        if max_urls:
            counter += 1
            if counter > max_urls:
                break

        if page.url in processed_urls or page.url in exclude_urls:
            continue

        processed_urls.append(page.url)

        if show_list:
            print(page.url)
        if show_report:
            result = process_url(browser, page.url)
            results.append(result)

    return results


def main(args):
    """
    Command-line entrypoint to process a URL or sitemap and show a report if needed.
    """
    browser = configure_browser()

    try:
        if args.url:
            result = process_url(browser, args.url)
            results = [result]
        else:
            results = process_sitemap(
                browser,
                site_url=args.siteurl,
                max_urls=args.max,
                show_list=args.list,
                show_report=args.report,
                exclude_urls=config.exclude_paths,
            )
    except Exception as e:
        logging.error('Exception: Error loading: %s', e)
    finally:
        browser.quit()

    if args.report or args.url:
        if results:
            analysis_report(results)
        else:
            logging.warn('No processed URLs to report on')


if __name__ == '__main__':
    main(process_arguments())
