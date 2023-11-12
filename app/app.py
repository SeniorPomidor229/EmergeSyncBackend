from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import user_router, workflow_router

app = FastAPI()

app.include_router(user_router.router, prefix="/user", tags=["User"])
app.include_router(workflow_router.workflow_router, prefix="/wrofkflow", tags=["Workflow"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)