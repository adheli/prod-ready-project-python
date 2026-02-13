from fastapi import FastAPI

from user_routes import router

app = FastAPI(title="User Service")
app.include_router(router)
