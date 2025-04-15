import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import argparse
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

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

def initialize_selenium_driver():
    logging.info("Initializing Selenium WebDriver.")
    try:
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(service=service, options=options)
        return driver
    except Exception as e:
        logging.exception("Failed to initialize Selenium WebDriver.")
        return None

def scrape_with_selenium(driver, url):
    try:
        driver.get(url)
        sleep(5) # TODO: Dynamic content loading
        return driver.page_source
    except Exception as e:
        logging.exception(f"Failed to scrape with Selenium: {e}")
        return None

def scrape_pdfs(base_url, depth, visited=None, pdf_urls=None, use_selenium=False, driver=None):
    if visited is None:
        visited = set()
    if pdf_urls is None:
        pdf_urls = []
    if depth < 0 or base_url in visited:
        logging.info(f"Skipping URL: {base_url} (Depth: {depth}, Visited: {base_url in visited})")
        return pdf_urls
    visited.add(base_url)

    logging.info(f"Scraping URL: {base_url} (Depth: {depth})")
    try:
        if use_selenium and driver:
            html_content = scrape_with_selenium(driver, base_url)
            if not html_content:
                return pdf_urls
            soup = BeautifulSoup(html_content, "html.parser")
        else:
            response = requests.get(base_url)
            if response.status_code != 200:
                logging.error(f"Failed to fetch: {base_url} (Status code: {response.status_code})")
                return pdf_urls
            soup = BeautifulSoup(response.text, "html.parser")

        base_netloc = urlparse(base_url).netloc
        base_domain = ".".join(base_netloc.split(".")[-2:])  # Extract the base domain (e.g., hpseb.in)
        links = soup.find_all("a", href=True)
        logging.info(f"Found {len(links)} links on {base_url}")
        if len(links) == 0:
            logging.info(f"No links found on {base_url}. Page content: {soup.prettify()}")
            
        for link in links:
            href = urljoin(base_url, link["href"])  # Resolve relative links
            logging.info(f"Found link: {href}")
            
            href_netloc = urlparse(href).netloc
            href_domain = ".".join(href_netloc.split(".")[-2:])  # Extract the domain of the href

            # Check if the href points to a PDF
            if href.endswith(".pdf"):
                pdf_urls.append(href)
                continue

            # Check if the link is within the same domain
            if href_domain != base_domain:
                logging.info(f"Skipping external link: {href} (Domain: {href_domain})")
                continue

            # Skip non-HTML links based on file extensions
            if not href.endswith((".htm", ".html")):
                logging.info(f"Skipping non-HTML link: {href}")
                continue

            # Recursively scrape HTML links
            scrape_pdfs(href, depth - 1, visited, pdf_urls, use_selenium, driver)

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
        "--export", action="store_true", help="Export all found PDF URLs to a text file (skips downloading)."
    )
    parser.add_argument(
        "--use-selenium", action="store_true", help="Use Selenium for scraping."
    )
    args = parser.parse_args()

    logging.info("Starting the web crawler application.")
    driver = None
    try:
        if args.use_selenium:
            driver = initialize_selenium_driver()
        pdf_urls = scrape_pdfs(args.url, args.depth, use_selenium=args.use_selenium, driver=driver)
        if args.export:
            export_pdf_urls(pdf_urls)
        else:
            for pdf_url in pdf_urls:
                download_pdf(pdf_url)
    except Exception as e:
        logging.exception(f"An error occurred during execution: {e}")
    finally:
        if driver:
            driver.quit()
            logging.info("Selenium WebDriver closed.")
    logging.info("Web crawler application finished execution.")

if __name__ == "__main__":
    main()
