from fastapi import APIRouter
from .auth import router as auth_router
from .policies_public import router as policies_public_router
from .categories import router as categories_router
from .admin_policies import router as admin_policies_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(policies_public_router)
api_v1_router.include_router(categories_router)
api_v1_router.include_router(admin_policies_router)