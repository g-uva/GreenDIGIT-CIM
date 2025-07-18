# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import metrics, query

app = FastAPI(title="Cloud Metrics API")

# Enable CORS for development/testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
app.include_router(query.router, prefix="/query", tags=["Query"])
