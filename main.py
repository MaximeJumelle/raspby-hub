import sys
import argparse

from src.logging import logger, initialize_logger
from src.install import install_raspbian, setup_raspbian


initialize_logger()

parser = argparse.ArgumentParser(description="Raspby Hub")
parser.add_argument("--install", action="store_true", help="Install Raspbian OS with utility tools and packages on a device.")
parser.add_argument("--setup", action="store_true", help="Setup utilities (SSH, WiFi and others) on a fresh install Raspbian OS.")
args = parser.parse_args()
    
if args.install:
    install_raspbian()
    sys.exit(0)  # Graceful shutdown
if args.setup:
    setup_raspbian()
    sys.exit(0)

logger.critical("No command provided. You must provide a specific command to interact with Raspby Hub.")
sys.exit(1)