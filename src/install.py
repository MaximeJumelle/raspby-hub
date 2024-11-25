import sys

import usb.core
import usb.util

from typing import Optional, List

from src.logging import logger

from src.utils import input_challenge
from src.models import USBDevice



def install_raspbian(
    device_port: Optional[str] = None,
):
    """Install Raspbian OS with utility tools and packages on a device."""
    logger.info("Scanning available USB devices...")

    # Find all USB devices
    raw_devices = usb.core.find(find_all=True)

    if raw_devices is None:
        logger.error("Could not list USB devices. Do you have sufficient permissions?")
        return
    
    usb_devices_list: List[USBDevice] = []

    # Print details of each device
    for raw_device in raw_devices:

        device = USBDevice(
            vendor_id=raw_device.idVendor,
            product_id=raw_device.idProduct,
            manufacturer_id=raw_device.iManufacturer,
        )

        try:
            # Retrieve descriptors
            device.manufacturer_name = usb.util.get_string(raw_device, raw_device.iManufacturer)
            device.name = usb.util.get_string(raw_device, raw_device.iProduct)
            usb_devices_list.append(device)
        except usb.core.USBError as e:
            logger.warning(f"Could not retrieve information on USB device '{device}' : {e}")
        except Exception:
            logger.warning(f"Could not retrieve information on USB device '{device}'. Do you have sufficient permissions?")

    if len(usb_devices_list) == 0:
        logger.critical("Could not list USB devices. Do you have sufficient permissions?")
        sys.exit(1)

    print("\nThe following USB devices were found.\n")
    for i, device in enumerate(usb_devices_list):
        print(f"[{i + 1}] {device}")

    print()
    choice = input_challenge(
        prompt="Please select the device you want to install Raspbian on : ",
        expected_type=int,
        validator=lambda x: 1 <= x <= len(usb_devices_list)
    )

    selected_device = usb_devices_list[choice - 1]
    format_choice = input_challenge(
        prompt="Do you want to format the device before installing Raspbian? (yes/no): ",
        expected_type=str,
        validator=lambda x: x.lower() in ["yes", "no"]
    )

    if format_choice.lower() == "yes":
        selected_device.format_device(filesystem="ext4")

    logger.info(f"Installing Raspbian on device '{selected_device}'...")
    selected_device.install_raspbian()
    