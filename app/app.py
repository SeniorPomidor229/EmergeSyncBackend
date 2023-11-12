from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import user_router, workflow_router

app = FastAPI()

app.include_router(user_router.router, prefix="/user", tags=["User"])
app.include_router(workflow_router.workflow_router, prefix="/workflow", tags=["Workflow"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from utils.jwt import decode_token
from routers.user_router import get_user_info

@app.get("/main")
async def read_main(token: str = Depends(decode_token)):
    return {"message": "Пиво по скидке"}

@app.get("/user/info")
async def read_user_info(token: str = Depends(decode_token)):
    return get_user_info(token)
