from loguru import logger
import sys

logger.remove()

logger.add(sys.stdout, level="DEBUG", colorize=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level}</level> | <cyan>{module}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>")


logger.add("src/logs/app.log", rotation="1 MB", retention="7 days")