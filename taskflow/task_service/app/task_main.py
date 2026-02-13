from fastapi import FastAPI

from task_routes import router

api = FastAPI(title="Task Service")
api.include_router(router)
