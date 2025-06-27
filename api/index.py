from fastapi import FastAPI  
import pystac_client  
from pydantic import BaseModel, Field

# The main application instance that Vercel will run  
app = FastAPI()

# Pydantic models for type checking the incoming request  
class STACRequest(BaseModel):  
    stac_url: str = Field(..., example="https://www.geo.admin.ch/en/rest-interface-stac-api")  
    query: dict | None = None  
    bbox: list[float] | None = None  
    datetime_str: str | None = None  
    collections: list[str] | None = None  
    limit: int = 10

# Your main tool endpoint, now at the root of the server  
@app.post("/tools/search_stac_items")  
def search_stac_items(request: STACRequest) -> dict:  
    """  
    Searches a STAC API endpoint based on provided parameters.  
    This is the function your LLM will call.  
    """  
    try:  
        client = pystac_client.Client.open(request.stac_url)  
          
        search = client.search(  
            collections=request.collections,  
            bbox=request.bbox,  
            datetime=request.datetime_str,  
            query=request.query,  
            limit=request.limit,  
        )  
          
        # Get results as a standard dictionary  
        items_dict = search.get_all_items_as_dict()  
        return items_dict

    except Exception as e:  
        # Return a structured error message  
        return {"error": f"Failed to query STAC API. Reason: {str(e)}"}

# A root endpoint for health checks to easily see if the server is running  
@app.get("/")  
def read_root():  
    return {"status": "STAC MCP Server is running"}
