from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import pandas as pd
import logging
import time
import random
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("scraper.log"),
        logging.StreamHandler()
    ]
)

class StealthFreePeopleScraper:
    def __init__(self, headless: bool = False):
        """Initialize with enhanced anti-detection for PerimeterX"""
        logging.info("Initializing Stealth Scraper...")
        
        self.data = []
        self.is_closed = False
        self.captcha_solved = False
        self.manual_continue = False
        self.session_file = "fp_session.json"
        self.headless = headless
        
        # Realistic user agents (recent versions only)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0'
        ]
        
        self.viewports = [
            {'width': 1920, 'height': 1080},
            {'width': 1366, 'height': 768},
            {'width': 1536, 'height': 864}
        ]
        
        self._setup_browser()
        self._start_input_listener()

    def _setup_browser(self):
        """Setup browser with maximum stealth against PerimeterX"""
        try:
            self.playwright = sync_playwright().start()
            
            # Minimal launch args to avoid detection
            launch_args = [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security'
            ]
            
            viewport = random.choice(self.viewports)
            user_agent = random.choice(self.user_agents)
            
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=launch_args,
                slow_mo=30  # Slight delay for more human-like behavior
            )
            
            # Context with realistic settings
            self.context = self.browser.new_context(
                viewport=viewport,
                user_agent=user_agent,
                locale='en-US',
                timezone_id='America/New_York',
                java_script_enabled=True,
                bypass_csp=False,  # Don't bypass CSP
                permissions=[],
                extra_http_headers={
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'Sec-Fetch-Dest': 'document',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-User': '?1',
                    'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-ch-ua-platform': '"Windows"'
                }
            )
            
            # Enhanced stealth script for PerimeterX bypass
            self.context.add_init_script("""
                // Remove webdriver property
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                // Override permissions
                const originalQuery = window.navigator.permissions.query;
                window.navigator.permissions.query = (parameters) => (
                    parameters.name === 'notifications' ?
                        Promise.resolve({ state: Notification.permission }) :
                        originalQuery(parameters)
                );
                
                // Mock plugins
                Object.defineProperty(navigator, 'plugins', {
                    get: () => [1, 2, 3, 4, 5]
                });
                
                // Mock languages
                Object.defineProperty(navigator, 'languages', {
                    get: () => ['en-US', 'en']
                });
                
                // Add Chrome object
                window.chrome = {
                    runtime: {}
                };
                
                // Override toString
                const originalToString = Function.prototype.toString;
                Function.prototype.toString = function() {
                    if (this === window.navigator.permissions.query) {
                        return 'function query() { [native code] }';
                    }
                    return originalToString.apply(this, arguments);
                };
                
                // Add realistic properties
                Object.defineProperty(navigator, 'hardwareConcurrency', {
                    get: () => 8
                });
                
                Object.defineProperty(navigator, 'deviceMemory', {
                    get: () => 8
                });
                
                Object.defineProperty(navigator, 'platform', {
                    get: () => 'Win32'
                });
                
                // Mask automation indicators
                delete navigator.__proto__.webdriver;
                
                // Override toJSON to hide automation
                Navigator.prototype.toJSON = undefined;
            """)
            
            self.page = self.context.new_page()
            self.page.set_default_timeout(60000)
            
            # Don't block resources - this can trigger detection
            # Let the page load naturally
            
            logging.info("Browser setup completed")
            
        except Exception as e:
            logging.error(f"Error setting up browser: {e}")
            raise

    def _start_input_listener(self):
        """Input listener for manual control"""
        def input_listener():
            while not self.is_closed:
                try:
                    cmd = input().strip().upper()
                    if cmd == 'Q':
                        print("Quit command received")
                        self.is_closed = True
                        break
                    elif cmd == 'S':
                        print(f"Status: {len(self.data)} products scraped")
                    elif cmd == 'C':
                        print("Continue - CAPTCHA marked as solved")
                        self.captcha_solved = True
                        self.manual_continue = True
                    elif cmd == 'H':
                        print("\nCommands: Q=Quit | S=Status | C=Continue (CAPTCHA solved) | H=Help")
                except:
                    pass
        
        self.input_thread = threading.Thread(target=input_listener, daemon=True)
        self.input_thread.start()

    def safe_navigate(self, url: str, max_attempts: int = 3) -> bool:
        """Navigate with retries"""
        for attempt in range(max_attempts):
            try:
                logging.info(f"Navigating to {url} (attempt {attempt + 1})")
                
                # Set random referer
                referers = [
                    "https://www.google.com/",
                    "https://www.freepeople.com/",
                    ""
                ]
                
                self.page.set_extra_http_headers({
                    'Referer': random.choice(referers)
                })
                
                self.page.goto(url, wait_until="networkidle", timeout=45000)
                
                # Wait for page to settle
                time.sleep(random.uniform(3, 5))
                
                # Check for CAPTCHA
                if self.detect_captcha():
                    logging.warning("CAPTCHA detected after navigation")
                    if not self.handle_captcha():
                        return False
                
                return True
                
            except PlaywrightTimeoutError:
                logging.warning(f"Navigation timeout (attempt {attempt + 1})")
                if attempt < max_attempts - 1:
                    time.sleep(random.uniform(3, 8))
                else:
                    return False
            except Exception as e:
                logging.error(f"Navigation error: {e}")
                if attempt < max_attempts - 1:
                    time.sleep(random.uniform(2, 6))
                else:
                    return False
        
        return False

    def detect_captcha(self) -> bool:
        """Detect PerimeterX CAPTCHA"""
        try:
            # Check for PerimeterX elements
            captcha_indicators = [
                'div#px-captcha',
                'div.px-captcha-container',
                'iframe[title*="Human verification"]',
                'div[id*="px"]',
                '[class*="px-captcha"]'
            ]
            
            for selector in captcha_indicators:
                try:
                    element = self.page.query_selector(selector)
                    if element and element.is_visible():
                        logging.warning(f"CAPTCHA detected via: {selector}")
                        return True
                except:
                    continue
            
            # Check page text
            try:
                body_text = self.page.evaluate("() => document.body.innerText.toLowerCase()")
                captcha_phrases = [
                    'press & hold',
                    'press and hold',
                    'verify you are',
                    'human verification',
                    'reference id'
                ]
                
                for phrase in captcha_phrases:
                    if phrase in body_text:
                        logging.warning(f"CAPTCHA detected via text: {phrase}")
                        return True
            except:
                pass
            
            # Check URL
            url = self.page.url.lower()
            if 'captcha' in url or 'px-captcha' in url:
                logging.warning("CAPTCHA detected in URL")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Error in CAPTCHA detection: {e}")
            return False

    def handle_captcha(self) -> bool:
        """Handle CAPTCHA with manual intervention"""
        print("\n" + "="*70)
        print("🚨 CAPTCHA DETECTED - Manual intervention required")
        print("="*70)
        print("Please solve the CAPTCHA in the browser window")
        print("After solving, type 'C' + ENTER to continue")
        print("Type 'Q' + ENTER to quit")
        print("="*70)
        
        self.captcha_solved = False
        self.manual_continue = False
        
        timeout = 900  # 15 minutes
        start_time = time.time()
        last_check = start_time
        
        while (time.time() - start_time) < timeout:
            if self.is_closed:
                return False
            
            # Check if CAPTCHA was solved
            if time.time() - last_check > 5:
                last_check = time.time()
                if not self.detect_captcha():
                    print("✅ CAPTCHA appears solved!")
                    self.captcha_solved = True
                    return True
            
            if self.manual_continue:
                self.manual_continue = False
                print("Verifying CAPTCHA solution...")
                time.sleep(2)
                
                if not self.detect_captcha():
                    print("✅ CAPTCHA solved successfully!")
                    return True
                else:
                    print("⚠️ CAPTCHA still present. Try again.")
            
            time.sleep(1)
        
        print("⏰ CAPTCHA timeout")
        return False

    def human_behavior(self, duration=10):
        """Simulate realistic human behavior"""
        try:
            end_time = time.time() + duration
            
            while time.time() < end_time and not self.is_closed:
                # Random mouse movement
                x = random.randint(100, 800)
                y = random.randint(100, 600)
                self.page.mouse.move(x, y, steps=random.randint(5, 15))
                time.sleep(random.uniform(0.5, 2))
                
                # Random scroll
                if random.random() < 0.4:
                    scroll = random.randint(-300, 300)
                    self.page.mouse.wheel(0, scroll)
                    time.sleep(random.uniform(1, 3))
                
                # Random hover
                if random.random() < 0.3:
                    try:
                        elements = self.page.query_selector_all('a, button, img')
                        if elements:
                            elem = random.choice(elements)
                            elem.hover(timeout=2000)
                            time.sleep(random.uniform(0.5, 1.5))
                    except:
                        pass
                
        except Exception as e:
            logging.warning(f"Human behavior error: {e}")

    def extract_product_data(self, url: str) -> List[Dict]:
        """Extract product data with stealth"""
        results = []
        
        try:
            if not self.safe_navigate(url):
                return [{"error": "Navigation failed", "url": url}]
            
            if self.detect_captcha():
                if not self.handle_captcha():
                    return [{"error": "CAPTCHA not resolved", "url": url}]
            
            # Simulate human browsing
            browse_time = random.uniform(5, 12)
            print(f"Simulating browsing ({browse_time:.1f}s)...")
            self.human_behavior(browse_time)
            
            # Check CAPTCHA again
            if self.detect_captcha():
                if not self.handle_captcha():
                    return [{"error": "CAPTCHA during extraction", "url": url}]
            
            print("Extracting data...")
            
            # Extract product info
            product_info = self.page.evaluate("""
                () => {
                    const data = {
                        title: "N/A",
                        colors: [],
                        ratings: "N/A",
                        reviews: "N/A",
                        price: "N/A",
                        description: "N/A"
                    };
                    
                    // Title
                    const titleEl = document.querySelector('h1.c-pwa-product-meta-heading, h1[data-testid="product-title"], h1');
                    if (titleEl) data.title = titleEl.innerText.trim();
                    
                    // Price
                    const priceEl = document.querySelector('[data-testid="product-price"], .c-pwa-product-price__current, .price');
                    if (priceEl) data.price = priceEl.innerText.trim();
                    
                    // Description
                    const descEl = document.querySelector('[data-testid="product-description"], .product-description');
                    if (descEl) data.description = descEl.innerText.trim().substring(0, 200);
                    
                    // Colors
                    const colorEls = document.querySelectorAll('img.o-pwa-color-swatch, [class*="color-swatch"]');
                    data.colors = Array.from(colorEls).map(el => 
                        el.getAttribute('alt') || el.getAttribute('title') || 'Unknown'
                    ).filter(c => c !== 'Unknown');
                    
                    if (data.colors.length === 0) data.colors = ['Default'];
                    
                    // Ratings
                    const ratingEl = document.querySelector('.c-pwa-review-stars, [aria-label*="star"]');
                    if (ratingEl) {
                        const label = ratingEl.getAttribute('aria-label');
                        if (label) {
                            const match = label.match(/(\d+\.?\d*)/);
                            if (match) data.ratings = match[1];
                        }
                    }
                    
                    // Reviews
                    const reviewEl = document.querySelector('.c-pwa-reviews-snippet__reviews-link-text');
                    if (reviewEl) {
                        const match = reviewEl.innerText.match(/(\d+)/);
                        if (match) data.reviews = match[1];
                    }
                    
                    return data;
                }
            """)
            
            # Process colors (limit to 23)
            colors = product_info.get('colors', ['Default'])[:23]
            
            for i, color in enumerate(colors):
                if self.is_closed:
                    break
                
                print(f"Processing color {i+1}/{len(colors)}: {color}")
                
                try:
                    # Click color if not default
                    if color != 'Default':
                        try:
                            color_el = self.page.query_selector(f"img[alt='{color}']")
                            if color_el and color_el.is_visible():
                                color_el.click(timeout=3000)
                                time.sleep(random.uniform(2, 4))
                        except:
                            logging.warning(f"Could not click color: {color}")
                    
                    # Check CAPTCHA
                    if self.detect_captcha():
                        if not self.handle_captcha():
                            break
                    
                    # Extract sizes using XPath for unavailable sizes
                    sizes_info = self.page.evaluate("""
                        () => {
                            const sizes = { all: [], unavailable: [] };
                            
                            // Get all sizes
                            const sizeEls = document.querySelectorAll('li.c-pwa-radio-boxes__item, .size-option');
                            sizeEls.forEach(el => {
                                const label = el.querySelector('label');
                                if (label) {
                                    const sizeText = label.innerText.trim();
                                    sizes.all.push(sizeText);
                                }
                            });
                            
                            // Get unavailable sizes using XPath
                            const unavailableIterator = document.evaluate(
                                '//input[@data-qa-is-available="false"]/following-sibling::label/text()',
                                document,
                                null,
                                XPathResult.ORDERED_NODE_SNAPSHOT_TYPE,
                                null
                            );
                            
                            for (let i = 0; i < unavailableIterator.snapshotLength; i++) {
                                const textNode = unavailableIterator.snapshotItem(i);
                                const sizeText = textNode.textContent.trim();
                                if (sizeText) {
                                    sizes.unavailable.push(sizeText);
                                }
                            }
                            
                            return sizes;
                        }
                    """)
                    
                    results.append({
                        'title': product_info['title'],
                        'color': color,
                        'all_sizes': ', '.join(sizes_info['all']) or 'N/A',
                        'unavailable_sizes': ', '.join(sizes_info['unavailable']),
                        'ratings': product_info['ratings'],
                        'reviews': product_info['reviews'],
                        'price': product_info['price'],
                        'description': product_info['description']
                    })
                    
                    # Delay between colors
                    if i < len(colors) - 1:
                        time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    logging.error(f"Error processing color {color}: {e}")
            
            return results
            
        except Exception as e:
            logging.error(f"Extraction error: {e}")
            return [{"error": str(e), "url": url}]

    def save_progress(self):
        """Save progress to CSV"""
        try:
            if not self.data:
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"free_people_{timestamp}.csv"
            
            df = pd.DataFrame(self.data, columns=[
                "Title", "Color", "All Sizes", "Unavailable Sizes",
                "Ratings", "Reviews", "Price", "Description"
            ])
            
            df.to_csv(filename, index=False, encoding="utf-8")
            print(f"✓ Saved: {filename} ({len(self.data)} products)")
            
        except Exception as e:
            logging.error(f"Save error: {e}")

    def run(self, csv_file: str):
        """Main execution"""
        try:
            df = pd.read_csv(csv_file)
            
            # Find URL column
            url_column = None
            for col in df.columns:
                if df[col].astype(str).str.contains('http').any():
                    url_column = col
                    break
            
            if not url_column:
                print("No URL column found")
                return
            
            urls = [url for url in df[url_column].dropna().tolist() 
                   if isinstance(url, str) and url.startswith('http')]
            
            print(f"Found {len(urls)} URLs")
            
            # Initialize with homepage
            print("Initializing session...")
            if self.safe_navigate("https://www.freepeople.com/"):
                self.human_behavior(random.uniform(5, 10))
            
            print("\n" + "="*70)
            print("SCRAPER STARTED | Commands: Q=Quit | S=Status | C=Continue | H=Help")
            print("="*70)
            
            # Process URLs
            for i, url in enumerate(urls):
                if self.is_closed:
                    break
                
                print(f"\n--- {i+1}/{len(urls)} ---")
                print(f"URL: {url}")
                
                results = self.extract_product_data(url)
                
                for result in results:
                    if 'error' not in result:
                        self.data.append([
                            result['title'], result['color'],
                            result['all_sizes'], result['unavailable_sizes'],
                            result['ratings'], result['reviews'],
                            result['price'], result['description']
                        ])
                        print(f"✓ {result['title']} - {result['color']}")
                    else:
                        print(f"✗ Error: {result.get('error')}")
                
                # Save periodically
                if i % 2 == 0 and i > 0:
                    self.save_progress()
                
                # Long delay between products
                if i < len(urls) - 1:
                    delay = random.uniform(3, 6)
                    print(f"Waiting {delay:.0f}s...")
                    for _ in range(int(delay)):
                        if self.is_closed:
                            break
                        time.sleep(1)
            
            print(f"\n✓ Completed! Total: {len(self.data)} products")
            
        except Exception as e:
            logging.error(f"Main error: {e}")
        finally:
            self.close()

    def close(self):
        """Cleanup"""
        print("Shutting down...")
        self.is_closed = True
        
        if self.data:
            self.save_progress()
        
        try:
            if hasattr(self, 'page'):
                self.page.close()
            if hasattr(self, 'context'):
                self.context.close()
            if hasattr(self, 'browser'):
                self.browser.close()
            if hasattr(self, 'playwright'):
                self.playwright.stop()
        except:
            pass
        
        print("Done")


if __name__ == "__main__":
    scraper = None
    try:
        scraper = StealthFreePeopleScraper(headless=False)
        scraper.run("link.csv")
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if scraper:
            scraper.close()
