import sys
import argparse

from src.logging import logger, initialize_logger
from src.install import install_raspbian


initialize_logger()

parser = argparse.ArgumentParser(description="Raspby Hub")
parser.add_argument("--install", action="store_true", help="Install Raspbian OS with utility tools and packages on a device.")
args = parser.parse_args()
    
if args.install:
    install_raspbian()
    sys.exit(0)  # Graceful shutdown

logger.critical("No command provided. You must provide a specific command to interact with Raspby Hub.")
sys.exit(1)