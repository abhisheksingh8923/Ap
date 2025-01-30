import os
import httpx
from fastapi import FastAPI, Depends, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

CLIENT_ID = os.getenv("FATSECRET_CLIENT_ID")
CLIENT_SECRET = os.getenv("FATSECRET_CLIENT_SECRET")
TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
SEARCH_URL = "https://platform.fatsecret.com/rest/server.api"

async def get_access_token() -> str:
    """Fetch OAuth 2.0 access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            TOKEN_URL,
            data={"grant_type": "client_credentials", "scope": "basic"},
            auth=(CLIENT_ID, CLIENT_SECRET),
        )

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to get access token: {response.text}")

    return response.json().get("access_token", "")

@app.get("/search-food")
async def search_food(query: str, token: str = Depends(get_access_token)):
    """Search for food items using FatSecret API."""
    params = {
        "method": "foods.search",
        "format": "json",
        "search_expression": query,
    }
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.get(SEARCH_URL, params=params, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to fetch food data: {response.text}")

    return response.json()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
