from fastapi import FastAPI
from routers import *

app = FastAPI()

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(access_rules_router, prefix="/access-rules", tags=["access_rules"])
app.include_router(profiles_router, prefix="/profile", tags=["profiles"])
app.include_router(products_router, prefix="/products", tags=["products"])
app.include_router(roles_router, prefix="/roles")
