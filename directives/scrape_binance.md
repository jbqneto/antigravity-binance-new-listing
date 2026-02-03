# Scrape Binance Listings

## Goal
Scrape the latest cryptocurrency listing announcements from Binance and extract relevant details (token name, dates, contract addresses).

## Tools
- `execution/scrape_binance.py`

## Inputs
- None (Target URL `https://www.binance.com/en/support/announcement/list/48?navId=48` is hardcoded in the script).

## Process
1.  Run the Python scraper script.
2.  The script navigates to the Binance announcement page.
3.  It filters announcements for the current and previous day (UTC).
4.  It extracts details including contract addresses (if matching hex patterns are found).

## Output
- **File**: `.tmp/binance_listings.json` (or custom path via `--output` arg)
- **Format**: JSON array of objects.
    ```json
    [
      {
        "title": "Listing Title",
        "url": "https://binance...",
        "date": "YYYY-MM-DD",
        "name": "Token Name",
        "token": "TICKER",
        "contracts_found": {
             "Network": "0xAddress"
        }
      }
    ]
    ```

## Dependencies
- `playwright` (Python)
- `chromium` (Playwright browser)

## Docker Deployment
To run this scraper in a Docker container:

1.  **Build the image**:
    ```bash
    docker build -t binance-scraper .
    ```

2.  **Run the container**:
    Mount the `.tmp` directory to access the output file.
    ```bash
    docker run --rm -v $(pwd)/.tmp:/app/.tmp binance-scraper
    ```

## Edge Cases / Notes
- **WAF/Bot Protection**: The script uses a manual `navigator.webdriver` override to bypass "Human Verification".
- **Empty Results**: If no announcements match today/yesterday, the output array will be empty.
