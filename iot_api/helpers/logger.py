import logging
import sys

from iot_api.core import config


def setup_logging():
    # Formatage des logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    logging.basicConfig(
        level=logging.DEBUG if config.APP_ENV == "dev" else logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Récupérer les loggers d'Uvicorn pour qu'ils utilisent notre config
    for name in ["uvicorn", "uvicorn.error", "uvicorn.access"]:
        uv_logger = logging.getLogger(name)
        uv_logger.handlers = logging.getLogger().handlers
        uv_logger.propagate = False
