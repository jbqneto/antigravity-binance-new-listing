import asyncio
import json
import re
from datetime import datetime
from playwright.async_api import async_playwright

async def scrape():
    announcements = []
    
    async with async_playwright() as p:
        # Launch browser with custom args to be more stealthy
        browser = await p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 720}
        )
        
        # Add stealth scripts manually
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()

        print("Navigating to Binance announcements...")
        await page.goto("https://www.binance.com/en/support/announcement/list/48?navId=48")
        await page.wait_for_load_state("networkidle")
        
        # Look for links
        links = await page.locator("a[href*='/support/announcement/detail/']").all()
        print(f"Found {len(links)} potential announcement links.")

        # Get today and yesterday dates (UTC)
        now = datetime.utcnow()
        today_str = now.strftime("%Y-%m-%d")
        
        # Filter only for today's announcements
        target_dates = [today_str]

        for link in links:
            # Get text and href
            title = await link.inner_text()
            href = await link.get_attribute("href")
            full_url = f"https://www.binance.com{href}"
            
            parent = link.locator("..")
            parent_text = await parent.inner_text()
            
            # Simple regex to find dates like YYYY-MM-DD
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})", parent_text)
            date_str = date_match.group(1) if date_match else None
            
            if date_str and date_str in target_dates:
                 announcements.append({
                    "title": title.strip(),
                    "url": full_url,
                    "date": date_str
                })
        
        results = []
        
        for item in announcements:
            print(f"Processing: {item['title']}")
            try:
                sub_page = await browser.new_page()
                await sub_page.goto(item['url'])
                await sub_page.wait_for_selector("body")
                
                text_content = await sub_page.locator("body").inner_text()
                
                # Extract Name and Token
                token_name = None
                token_ticker = None
                title_match = re.search(r"Will (?:List|Add) (.*?) \((.*?)\)", item['title'])
                if title_match:
                    token_name = title_match.group(1).strip()
                    token_ticker = title_match.group(2).strip()
                
                # Extract Contracts
                contracts = {}
                for match in re.finditer(r"0x[a-fA-F0-9]{40}", text_content):
                    address = match.group(0)
                    start_pos = match.start()
                    context_start = max(0, start_pos - 150)
                    context_text = text_content[context_start:start_pos]
                    
                    # Context analysis to find strictly the CLOSEST network label
                    
                    # Define network patterns map
                    network_patterns = {
                        "Ethereum": r"Ethereum|ERC20|ETH|ERC-20",
                        "BNB Smart Chain": r"BNB Smart Chain|BEP20|BSC|BEP-20",
                        "Arbitrum": r"Arbitrum|ARB",
                        "Polygon": r"Polygon|MATIC",
                        "Optimism": r"Optimism|OP",
                        "Base": r"Base",
                        "Ronin": r"Ronin|RON",
                        "Solana": r"Solana|SOL"
                    }
                    
                    detected_network = "Unknown"
                    closest_match_pos = -1
                    
                    for net_name, pattern in network_patterns.items():
                        # Find all matches of this network pattern in the context
                        for match in re.finditer(pattern, context_text, re.IGNORECASE):
                            if match.start() > closest_match_pos:
                                closest_match_pos = match.start()
                                detected_network = net_name
                    
                    # Only add if we found a network or strictly new address
                    # If we detected a network, verify we don't overwrite with Unknown unless necessary (but here we default to Unknown and only update if found)
                    
                    if detected_network != "Unknown":
                         contracts[detected_network] = address
                    elif address not in contracts.values():
                         # If unknown network, maybe append with a generic key or just skip if we want to be strict?
                         # Let's add it as "Unknown" or "Unknown_1", "Unknown_2" etc if we want to keep it.
                         # For now, following logic of 'contracts' dict, we can't have duplicate keys.
                         # Let's just key it by address if unknown? No, requirement is Network: Address.
                         # If unknown, maybe "Contract": address
                         if "Unknown" not in contracts:
                             contracts["Unknown"] = address
                         else:
                             # Append? or just ignore secondary unknown?
                             pass

                clean_title = item['title'].replace(item['date'], "").strip()
                
                result_obj = {
                    "title": clean_title,
                    "url": item['url'],
                    "date": item['date'],
                    "contracts_found": contracts
                }
                
                if token_name:
                    result_obj["name"] = token_name
                if token_ticker:
                    result_obj["token"] = token_ticker
                    
                results.append(result_obj)
                await sub_page.close()
            except Exception as e:
                print(f"Error processing {item['url']}: {e}")

        await browser.close()
        return results

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Scrape Binance Listings")
    parser.add_argument("--output", default=".tmp/binance_listings.json", help="Path to save the output JSON")
    args = parser.parse_args()
    
    data = asyncio.run(scrape())
    
    with open(args.output, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Done. Saved to {args.output}")
