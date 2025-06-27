from fastapi import FastAPI  
import requests  
from pydantic import BaseModel, Field
from typing import Optional, List

# The main application instance that Vercel will run  
app = FastAPI()

# Pydantic models for type checking the incoming request  
class STACRequest(BaseModel):  
    stac_url: str = Field("https://data.geo.admin.ch/api/stac/v0.9/")  
    query: Optional[dict] = None  
    bbox: Optional[List[float]] = None  
    datetime_str: Optional[str] = None  
    collections: Optional[List[str]] = None  
    limit: int = 10

# Your main tool endpoint, now at the root of the server  
@app.post("/tools/search_stac_items")  
def search_stac_items(request: STACRequest) -> dict:  
    """  
    Searches a STAC API endpoint based on provided parameters.  
    This is the function your LLM will call.  
    """  
    try:
        # Ensure the URL ends with a slash and add the /search path
        search_url = request.stac_url.rstrip('/') + '/search'

        # Build the payload for the STAC API search, respecting the spec's 'datetime' field
        payload = {
            "collections": request.collections,
            "bbox": request.bbox,
            "datetime": request.datetime_str,
            "query": request.query,
            "limit": request.limit
        }

        # Filter out any None values so they are not sent in the request body
        payload = {k: v for k, v in payload.items() if v is not None}

        # Make the POST request to the STAC search endpoint
        response = requests.post(search_url, json=payload)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        return response.json()

    except requests.exceptions.RequestException as e:
        # Handle connection errors, timeouts, etc.
        return {"error": f"Failed to connect to STAC API. Reason: {str(e)}"}
    except Exception as e:
        # Handle other potential errors, e.g., JSON decoding
        return {"error": f"An unexpected error occurred. Reason: {str(e)}"}

# A root endpoint for health checks to easily see if the server is running  
@app.get("/")  
def read_root():  
    return {"status": "STAC MCP Server is running"}
