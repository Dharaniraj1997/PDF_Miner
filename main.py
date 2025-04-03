import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import argparse
import logging

OUTPUT_DIR = os.path.join(os.getcwd(), "pdfs")
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler() 
    ]
)

def download_pdf(url):
    logging.info(f"Attempting to download PDF: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        filename = os.path.join(OUTPUT_DIR, url.split("/")[-1])
        with open(filename, "wb") as f:
            f.write(response.content)
        logging.info(f"Downloaded: {filename}")
    else:
        logging.error(f"Failed to download: {url} (Status code: {response.status_code})")

def export_pdf_urls(urls, output_file="pdf_urls.txt"):
    logging.info(f"Exporting PDF URLs to {output_file}")
    try:
        if os.path.exists(output_file):
            logging.info(f"Removing existing file: {output_file}")
            os.remove(output_file)
        with open(output_file, "w") as f:
            for url in urls:
                f.write(url + "\n")
        logging.info(f"Exported {len(urls)} PDF URLs to {output_file}")
    except Exception as e:
        logging.exception(f"Failed to export PDF URLs: {e}")

def scrape_pdfs(base_url, depth, visited=None, pdf_urls=None):
    if visited is None:
        visited = set()
    if pdf_urls is None:
        pdf_urls = []
    if depth < 0 or base_url in visited:
        logging.debug(f"Skipping URL: {base_url} (Depth: {depth}, Visited: {base_url in visited})")
        return pdf_urls
    visited.add(base_url)

    logging.info(f"Scraping URL: {base_url} (Depth: {depth})")
    try:
        response = requests.get(base_url)
        if response.status_code != 200:
            logging.error(f"Failed to fetch: {base_url} (Status code: {response.status_code})")
            return pdf_urls
        soup = BeautifulSoup(response.text, "html.parser")
        for link in soup.find_all("a", href=True):
            href = urljoin(base_url, link["href"])
            if href.endswith(".pdf"):
                pdf_urls.append(href)
            elif href.startswith(base_url):  # Only follow links within the same domain
                scrape_pdfs(href, depth - 1, visited, pdf_urls)
    except Exception as e:
        logging.exception(f"Error scraping {base_url}: {e}")
    return pdf_urls

def main():
    parser = argparse.ArgumentParser(
        description="Download or export all PDF files from a website."
    )
    parser.add_argument("url", help="The base URL to scrape.")
    parser.add_argument("depth", type=int, help="The depth to scrape.")
    parser.add_argument(
        "--download", action="store_true", help="Download all found PDF files."
    )
    parser.add_argument(
        "--export", action="store_true", help="Export all found PDF URLs to a text file."
    )
    args = parser.parse_args()

    logging.info("Starting the web crawler application.")
    try:
        pdf_urls = scrape_pdfs(args.url, args.depth)
        if args.download:
            for pdf_url in pdf_urls:
                download_pdf(pdf_url)
        if args.export:
            export_pdf_urls(pdf_urls)
    except Exception as e:
        logging.exception(f"An error occurred during execution: {e}")
    logging.info("Web crawler application finished execution.")

if __name__ == "__main__":
    main()
