import os
from fastapi import FastAPI
from dotenv import load_dotenv
from endpoint import router as api_router
from chat_history import history_app as hisRouter
from fastapi.middleware.cors import CORSMiddleware
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

load_dotenv()

app = FastAPI()


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# origins = [
#     "http://localhost:3000",
#     "http://localhost:2020", 
#     "http://127.0.0.1:2020", 
#     "http://192.168.231.2:8501"
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
app.include_router(api_router, prefix="/api")
app.include_router(hisRouter, prefix="/api")
