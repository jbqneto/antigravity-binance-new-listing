# Binance New Listing Scraper

A specialized tool to automate the detection of new cryptocurrency listings on Binance. This project navigates the Binance Announcements page, filters for recent listings, and extracts key token details including contract addresses across various networks.

## 🚀 Features

*   **Automated Scraping**: Uses `playwright` to navigate and scrape dynamic content.
*   **Smart Filtering**: Automatically targets announcements from the current and previous day.
*   **Deep Extraction**:
    *   Extracts **Token Name** and **Ticker** (e.g., "Zama" / "ZAMA").
    *   Identifies **Contract Addresses** mapped to their specific networks (Ethereum, BNB Smart Chain, Solana, etc.).
    *   Handles multiple contracts per listing correctly.
*   **WAF Bypass**: Implements manual stealth context to bypass Binance's "Human Verification" challenges.
*   **Docker Ready**: Fully containerized with `Dockerfile` and `docker-compose.yml` for easy deployment (Portainer compatible).
*   **API Interface**: Exposes a simple FastAPI endpoint to trigger scrapes.

## 🛠 Project Structure

This project follows a 3-Layer Agentic Architecture:

*   **`directives/`**: Standard Operating Procedures (SOPs) and documentation.
*   **`execution/`**: Deterministic Python scripts (`scrape_binance.py`) and API logic (`api.py`).
*   **`.tmp/`**: Directory for intermediate storage of scraped JSON files.

## 📦 Installation & Usage

### Option 1: Docker (Recommended)

#### Using Docker Compose (Portainer)
The easiest way to run the service.

```bash
docker-compose up -d
```

The service will be available on port `8000`.

- **Health Check**: `GET http://localhost:8000/health`
- **Trigger Scrape**: `POST http://localhost:8000/scrape`

#### Manual Docker Run
```bash
# Build the image
docker build -t binance-scraper .

# Run the container (mounting .tmp to see output locally)
docker run --rm -v $(pwd)/.tmp:/app/.tmp -p 8000:8000 binance-scraper
```

### Option 2: Local Python Environment

**Prerequisites**: Python 3.10+

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    playwright install chromium
    ```

2.  **Run the Scraper Directly**:
    ```bash
    python3 execution/scrape_binance.py --output .tmp/binance_listings.json
    ```

3.  **Run the API Server**:
    ```bash
    uvicorn execution.api:app --host 0.0.0.0 --port 8000
    ```

## 📄 Output Format

The scraper produces a clean JSON output found in `.tmp/binance_listings.json` (or via API response):

```json
[
  {
    "title": "Binance Will List Zama (ZAMA) with Seed Tag Applied",
    "url": "https://www.binance.com/en/support/announcement/detail/...",
    "date": "2026-02-02",
    "name": "Zama",
    "token": "ZAMA",
    "contracts_found": {
      "Ethereum": "0xa12cc123ba206d4031d1c7f6223d1c2ec249f4f3",
      "BNB Smart Chain": "0x6907a5986c4950bdaf2f81828ec0737ce787519f"
    }
  }
]
```

## ⚠️ Notes

*   **Stealth Mode**: The browser runs in headless mode but includes specific overrides (`navigator.webdriver`) to avoid detection.
*   **Rate Limits**: Please be mindful of scraping frequency to avoid IP bans from Binance.
