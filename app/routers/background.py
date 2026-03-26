import os
import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from app.schemas.background import Create

load_dotenv()
BASE_URL = os.getenv("BACKGROUND_URL")
router = APIRouter(prefix="/background", tags=["background"])

@router.post("/")
async def create(data: Create):
    url = f"{BASE_URL}/background-checks"

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data.model_dump())

    if response.status_code not in [200, 201]:
        raise HTTPException(status_code=500, detail="Failed to create post")

    return response.json()

@router.get("/")
async def get_checks(employeeId: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/background-checks?employeeId={employeeId}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()

@router.get("/{checkId}")
async def get_check(checkId: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/background-checks/{checkId}")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())

    return response.json()