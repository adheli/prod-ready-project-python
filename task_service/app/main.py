"""
Main entry point for the Task Service API.
This module initializes the FastAPI application and includes all defined routers.
"""
import logging
import os
import sys

from fastapi import FastAPI

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.info(PROJECT_ROOT)
sys.path.append(PROJECT_ROOT)

from app.task_routes import router

app = FastAPI(title="Task Service")
app.include_router(router)
