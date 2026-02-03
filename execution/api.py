from fastapi import FastAPI, HTTPException
from execution.scrape_binance import scrape
import asyncio

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/scrape")
async def run_scrape():
    try:
        data = await scrape()
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
