import json

import requests
from bs4 import BeautifulSoup
from tenacity import retry, wait_fixed, stop_after_attempt
import time

from app.cache import Cache


class Scraper:
    def __init__(self, base_url, page_limit=None, retry_attempts=3, retry_wait=2):
        self.base_url = base_url
        self.page_limit = page_limit
        self.retry_attempts = retry_attempts
        self.retry_wait = retry_wait
        self.session = requests.Session()
        self.redis_client = Cache()

    @retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
    def fetch_html(self, url):
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                return response.content
            else:
                raise requests.RequestException(f"Failed to fetch {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching {url}: {str(e)}")
            raise e

    def scrape_products(self):
        scraped_data = []
        page_number = 1
        while not self.page_limit or page_number <= self.page_limit:
            url = f"{self.base_url}page/{page_number}"
            print(url)
            try:
                html_content = self.fetch_html(url)
                if html_content:
                    soup = BeautifulSoup(html_content, 'html.parser')
                    products = soup.select("ul.products li.product")
                    for product in products:
                        # print(f"product --------->{product}")  # Print to debug the selected products
                        product_title_element = product.select_one("div.mf-product-thumbnail img")
                        product_price_element = product.select_one("span.woocommerce-Price-amount.amount")
                        product_image_element = product.select_one("img")

                        if product_title_element and product_price_element and product_image_element:
                            product_title = product_title_element.get("title", "").strip()
                            product_price = float(product_price_element.text.strip().replace('₹', '').replace(',', ''))
                            product_image = product_image_element.get("src")
                            product_data = {
                                "product_title": product_title,
                                "product_price": product_price,
                                "path_to_image": product_image
                            }
                            scraped_data.append(product_data)
                            cached_product_price = self.redis_client.load(product_title)
                            if cached_product_price == product_price:
                                print(f"No price change for {product_title}. Skipping update.")
                                continue

                            self.redis_client.save(product_data)

                    page_number += 1
                    time.sleep(1)  # Add a small delay to avoid hitting the server too frequently
                else:
                    break
            except requests.RequestException:
                print(f"Failed to fetch page {page_number} after retries.")
                break
        return scraped_data
