from fastapi import APIRouter
# from handlers import user_router, wallet_router, license_router, product_router, root_router
# from handlers.service_handlers import service_router
from handlers import root_router


main_router = APIRouter(prefix="/api/v1")
# api_router.include_router(user_router, prefix="/users")
# api_router.include_router(wallet_router, prefix="/wallet")
# api_router.include_router(license_router, prefix="/license")
# api_router.include_router(product_router, prefix="/product")
# api_router.include_router(service_router, prefix="/service")
main_router.include_router(root_router)
