import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from utils import logger
import importlib


STEPS = ["01_ingest", "02_quality", "03_transform", "04_notify"]


def run():
    logger.info("====== Pipeline Sport Data Solution : démarrage ======")
    for step in STEPS:
        logger.info(f"--- Étape : {step} ---")
        module = importlib.import_module(step)
        module.run()
    logger.info("====== Pipeline terminé avec succès ======")


if __name__ == "__main__":
    run()
