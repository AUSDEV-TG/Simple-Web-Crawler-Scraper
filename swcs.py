import time
import argparse
import os
import requests
import http.client
import urllib.request
from urllib.error import HTTPError
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# Simple-Web-Crawler & Scraper Script
# Author: Tom Green
# Date Created: 10/01/2020


def process_url(url, path, ignore):
    parsed_url = urlparse(url)
    result = requests.get(url)

    if result.status_code != http.client.OK:
        print(f"{url} : {result.status_code}")
        return []

    if "html" not in result.headers['Content-type']:
        print(f"{url} is not an html document.")
        return []

    page = BeautifulSoup(result.text, 'lxml')

    return get_urls(parsed_url, page, path, ignore)


def get_urls(parsed_url, page, url_path, ignore):
    urls = []

    # Iterate through the hyperlinks on the page
    for element in page.find_all('a'):
        # Get the link from the hyperlink
        link = element.get("href")
        if not link:
            continue

        # Ignore internal links
        if '#' in link:
            continue

        # Modify local links
        if not link.startswith("http"):
            path = urljoin(parsed_url.path, link)
            link = f"{parsed_url.scheme}://{parsed_url.netloc}{path}"

        # Ignore links that our outside the original site's domain
        if parsed_url.netloc not in link:
            continue

        if url_path is not None:
            # Ignore links that aren't in the specified path
            if url_path not in link:
                continue

        if ignore is not None:
            # Ignore links that contain a specified keyword
            if ignore in link:
                continue

        urls.append(link)

    return urls


def save_html(url, output):
    # Get the html source from the url
    source = urllib.request.urlopen(url).read()

    # Create a safe name for the file
    fileName = url.split('/')[-2].replace(' ', '_') + '.html'

    # Save the source to the output path
    with open("{}\{}".format(output, fileName), 'wb') as file:
        file.write(source)


def main(url, output, ignore, path):
    saved_files = set()
    to_check = [url]
    max_checks = 10

    # Variable to store time at the beginning of the loop
    start = time.time()

    try:
        while to_check and max_checks:
            link = to_check.pop(0)
            links = process_url(link, path, ignore)
            saved_files.add(link)

            for link in links:
                if link not in saved_files:
                    saved_files.add(link)
                    to_check.append(link)
                    print(f"Saving Page {len(to_check):>3} : {link}")
                    save_html(link, output)

            max_checks -= 1
    except HTTPError:
        print("\nFatal: 404 Encountered...\n")

    # Variable to store time at the end of the loop
    end = time.time()

    # Variable to store the difference between the start and end times
    elapsed_time = end - start

    # Calculate minutes and seconds from the elapsed_time variable
    elapsed_mins = elapsed_time // 60
    elapsed_seconds = elapsed_time - 60 * elapsed_mins

    # Print how long the crawling and scraping took
    print(
        f"Completed after {elapsed_mins} minutes, {elapsed_seconds} seconds.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # The url to crawl when the script is executed
    parser.add_argument("-u", "--url", type=str,
                        help="url to crawl")

    # The output path where the scraped html files will be stored
    parser.add_argument("-o", "--output", default=os.getcwd(),
                        type=str, help="output path")

    # The keywords to ignore in the collected urls
    parser.add_argument("-i", "--ignore",  default="/print/",
                        type=str, help="keyword for ignoring particular pages")

    # The path of a url to be crawled
    parser.add_argument("-p", "--path", type=str,
                        help="the path of the url to be crawled")

    args = parser.parse_args()

    main(args.url, args.output, args.ignore, args.path)
