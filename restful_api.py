from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import json

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI()

# CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simulasi data dari file JSON
with open('workflow/Simple_Expression.json') as f:
    simple_expression_data = json.load(f)

with open('workflow/Clothes_Swapping.json') as f:
    clothes_swapping_data = json.load(f)

@app.get("/api/simple-expression")
async def get_simple_expression():
    """Endpoint to get Simple Expression data."""
    return JSONResponse(content=simple_expression_data)

@app.get("/api/clothes-swapping")
async def get_clothes_swapping():
    """Endpoint to get Clothes Swapping data."""
    return JSONResponse(content=clothes_swapping_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080)