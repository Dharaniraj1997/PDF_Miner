# Web Crawler for PDF Downloads

This is a Python-based web crawler that downloads all PDF files from a given website up to a specified depth.

## Installation

```bash
git clone "https://github.com/Dharaniraj1997/Web_Crawler"
cd Web_Crawler
pip install -r requirements.txt
```

## Usage

Run the script with the following command:

```bash
python main.py <url> <depth> [options]
```

- `<url>`: The base URL to start scraping.
- `<depth>`: The depth of recursion for scraping.

### Options

- `--export`: Export all found PDF URLs to a text file (`pdf_urls.txt`). This skips downloading the PDFs.
- `--use-selenium`: Use Selenium for scraping instead of `requests` and `BeautifulSoup`. This is useful for websites that heavily rely on JavaScript.

### Examples

1. Download all PDFs from a website up to a depth of 2 (default behavior):

   ```bash
   python main.py https://example.com 2
   ```

2. Export all PDF URLs to a text file (skips downloading):

   ```bash
   python main.py https://example.com 2 --export
   ```

3. Use Selenium for scraping and download PDFs:
   ```bash
   python main.py https://example.com 2 --use-selenium
   ```

## License

This project is licensed under the MIT License.
