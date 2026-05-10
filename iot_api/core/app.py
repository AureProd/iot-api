import logging

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from iot_api.core import config
from iot_api.core.lifespan import app_lifespan
from iot_api.helpers.logger import setup_logging
from iot_api.routes.oauth import router as auth_router
from iot_api.routes.smart_home import router as smart_home_router

setup_logging()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="IOT API",
    version="0.1.0",
    contact={
        "name": "AureProd",
        "email": "aureprod0@gmail.com",
    },
    docs_url="/api/iot/docs",
    openapi_url="/api/iot/openapi.json",
    lifespan=app_lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
router = APIRouter(prefix="/api/iot")
router.include_router(auth_router)
router.include_router(smart_home_router)

app.include_router(router)

logger.info("IOT API started and ready.")

for device in config.DEVICES.values():
    logger.info(f"Device '{device.name}' with ID '{device.id}' and type '{device.type}' ready.")
