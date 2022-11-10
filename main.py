import logging

from gui import Login
from config.log_config import logger_config

if __name__ == "__main__":
    logger_config()
    logging.info("client start")
    login = Login()
    login.run()
