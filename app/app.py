from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routers import user_router, workflow_router, item_router, log_router,role_router

app = FastAPI()

app.include_router(user_router.router, prefix="/user", tags=["User"])
app.include_router(workflow_router.workflow_router, prefix="/workflow", tags=["Workflow"])
app.include_router(item_router.item_router, prefix="/workflow_item", tags=["WorkflowItem"])
app.include_router(log_router.log_router, prefix="/workflow_log", tags=["WorkflowLog"])
app.include_router(role_router.role_router, prefix="/role", tags=["Role"])
app.include_router(role_router.rule_router, prefix="/role", tags=["Rules"])

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

