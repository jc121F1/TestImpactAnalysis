import logging
import sys

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatting = logging.Formatter('[%(asctime)s][test_impact_analyser][%(levelname)s] %(message)s')
    handler.setFormatter(formatting)
    logger.addHandler(handler)
    return logger

def get_handler(name: str) -> logging.StreamHandler:
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatting = logging.Formatter(
        '[%(asctime)s][test_impact_analyser][%(levelname)s] %(message)s')
    handler.setFormatter(formatting)
    return handler