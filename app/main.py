from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel  # Make sure BaseModel is imported

from app.scraper import Scraper
from app.db import Database
from app.notifier import Notifier
from app.settings import Settings

from typing import Optional

app = FastAPI()

AUTH_TOKEN = "your-auth-token"


class ScrapingInput(BaseModel):
    page_limit: Optional[int] = None


def get_token_header(authorization: str = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=403, detail="Authorization header missing")
    return authorization


@app.post("/scrape")
def scrape_website(params: ScrapingInput, token: str = Depends(get_token_header)):
    if token != f"Bearer {AUTH_TOKEN}":
        raise HTTPException(status_code=401, detail="Unauthorized")

    scraper_settings = Settings(page_limit=params.page_limit)
    scraper = Scraper(base_url="https://dentalstall.com/shop/", page_limit=scraper_settings.page_limit)
    scraped_data = scraper.scrape_products()

    database = Database(filename="scraped_data.json")
    database.save_to_json(scraped_data)

    notifier = Notifier()
    notifier.notify_scraping_status(len(scraped_data))

    return {"message": "Scraping completed successfully."}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
