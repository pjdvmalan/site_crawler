#!/usr/bin/env python
"""
Site crawler application.
"""
import traceback

from etc import config
from lib import report_results, configure_browser, logging, process_arguments, process_url, process_sitemap


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
                exclude_urls=config.EXCLUDE_PATHS,
            )
    except Exception as ex:
        logging.error('Exception: %s', ex)
        traceback.print_exc()
    finally:
        browser.quit()

    if args.report or args.url:
        if not args.skip_analysis:
            if results:
                source_url_path = args.url if args.url else args.siteurl if args.siteurl else config.TARGER_URL
                report_results(source_url_path.lower(), results)

            else:
                logging.warning('No processed URLs to report on')

        else:
            logging.warning('Argument -a / --skip_analysis used; nothing to report on.')


if __name__ == '__main__':
    main(process_arguments())
