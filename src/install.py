import sys

import usb.core
import usb.util

from typing import Optional

from src.logging import logger

from .utils import input_challenge


def install_raspbian(
    device_port: Optional[str] = None,
):
    """Install Raspbian OS with utility tools and packages on a device."""
    logger.info("Scanning available USB devices...")
        
    # Find all USB devices
    devices = usb.core.find(find_all=True)

    if devices is None:
        logger.error("Could not list USB devices. Do you have sufficient permissions?")
        return
    
    usb_devices_list = []

    # Print details of each device
    for device in devices:
        device_id = f"{device.idVendor:04x}:{device.idProduct:04x}"
        try:
            # Retrieve descriptors
            manufacturer = usb.util.get_string(device, device.iManufacturer)
            if manufacturer is None:
                manufacturer = "Unknown"
            product = usb.util.get_string(device, device.iProduct)
            usb_devices_list.append(f"{product} ({manufacturer}) - {device_id}")
        except usb.core.USBError as e:
            logger.warning(f"Could not retrieve information on USB device '{device_id}' : {e}")
        except Exception:
            logger.warning(f"Could not retrieve information on USB device '{device_id}'. Do you have sufficient permissions?")

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