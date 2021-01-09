#!/usr/bin/env python
"""
Site crawler application.
"""
from usp.tree import sitemap_tree_for_homepage as site_map_tree

from etc import config
from lib import analysis_report, configure_browser, logging, process_arguments, process_url


def process_sitemap(browser, site_url, max_urls, show_list, skip_analysis, exclude_urls):
    results = []

    counter = 0
    processed_urls = []

    target_url = site_url if site_url else config.target_url
    site_map = site_map_tree(target_url)

    for page in site_map.all_pages():
        if page.url in processed_urls or page.url in exclude_urls:
            continue

        # max_urls apply only to non duplicate/excluded URLs.
        if max_urls:
            counter += 1
            if counter > max_urls:
                break

        processed_urls.append(page.url)

        if show_list:
            print(page.url)
        if not skip_analysis:
            results.append(process_url(browser, page.url))

    return results


def main(args):
    """
    Command-line entrypoint to process a URL or sitemap and show a report if needed.
    """
    browser = configure_browser()
    results = None

    try:
        if args.url:
            results = [process_url(browser, args.url)]
        else:
            results = process_sitemap(
                browser,
                site_url=args.siteurl,
                max_urls=args.max,
                show_list=args.list,
                skip_analysis=args.skip_analysis,
                exclude_urls=config.exclude_paths,
            )
    except Exception as e:
        logging.error('Exception: Error loading: %s', e)
    finally:
        browser.quit()

    if args.report or args.url:
        if not args.skip_analysis:
            if results:
                analysis_report(results)
            else:
                logging.warning('No processed URLs to report on')
        else:
            logging.warning('Argument -a / --skip_analysis used; nothing to report on.')


if __name__ == '__main__':
    main(process_arguments())
