import logging
import os
import sys

from fastapi import FastAPI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.info(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT)

from app.user_routes import router

app = FastAPI(title="User Service")
app.include_router(router)
