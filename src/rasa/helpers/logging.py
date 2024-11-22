from typing import Dict, Any, Text
from logging import Logger
import logging
import os

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "FATAL": logging.FATAL,
}


def setup_logger(logger: Logger, config: Dict[Text, Any]) -> None:
    log_level = logging.INFO
    if config["logLevel"] in LOG_LEVELS.keys():
        log_level = LOG_LEVELS[config["logLevel"]]

    logfile_path = os.path.join(config["directory"], config["name"])

    if not os.path.exists(config["directory"]):
        os.makedirs(config["directory"])

    logger.setLevel(log_level)
    root_logger = logger.root
    root_logger.setLevel(log_level)
    formatter = logging.Formatter("%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s")
    root_logger.handlers[0].setFormatter(formatter)
    root_logger.handlers[0].setLevel(log_level)
    fh = logging.handlers.TimedRotatingFileHandler(logfile_path + ".log", when="midnight", encoding="utf-8")
    fh.setLevel(log_level)
    fh.suffix = "%Y%m%d"
    fh.namer = lambda name: logfile_path + "." + name[name.rfind(".") + 1 :] + ".log"
    fh.setFormatter(formatter)
    logger.addHandler(fh)
