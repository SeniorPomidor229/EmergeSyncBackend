from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user_router

app = FastAPI()

app.include_router(user_router.router, prefix="/user", tags=["User"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)