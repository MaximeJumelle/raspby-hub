import requests
import sys
import os
import pyudev
import itertools
import re

from typing import Optional, List
from datetime import datetime

from src.logging import logger
from src.utils import input_challenge, run_subprocess


class USBDevice:
    def __init__(self, vendor_id: int, product_id: int, manufacturer_id: Optional[str] = None):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.manufacturer_id = manufacturer_id

        self.name: Optional[str] = None
        self.manufacturer_name: Optional[str] = None

    def __repr__(self):
        return f"{self.name} ({self.manufacturer_name}) - {self.vendor_id:04x}:{self.product_id:04x}"
    
    def find_dev_name(self) -> Optional[str]:
        """The the dev name (/dev/sda) associated to this device."""
        for udev in pyudev.Context().list_devices(subsystem='block', DEVTYPE='disk'):
            found_vendor_id: Optional[int] = udev.get('ID_VENDOR_ID')
            found_model_id: Optional[int] = udev.get('ID_MODEL_ID')
            if found_vendor_id is not None and str(found_vendor_id) == f"{self.vendor_id:04x}" \
            and found_model_id is not None and str(found_model_id) == f"{self.product_id:04x}" \
            and "ID_PART_TABLE_TYPE" in udev:
                return udev.get('DEVNAME')
    
    def find_dev_names(self) -> List[str]:
        """Find the dev names (/dev/sda1, /dev/sda2, ...) associated to this device."""
        udev_names: List[str] = []
        for udev in pyudev.Context().list_devices(subsystem='block', DEVTYPE='partition'):
            found_vendor_id: Optional[int] = udev.get('ID_VENDOR_ID')
            found_model_id: Optional[int] = udev.get('ID_MODEL_ID')
            if found_vendor_id is not None and str(found_vendor_id) == f"{self.vendor_id:04x}" \
                and found_model_id is not None and str(found_model_id) == f"{self.product_id:04x}" \
            and "ID_PART_TABLE_TYPE" in udev:
                udev_names.append(udev.get('DEVNAME'))
        return udev_names
    
    def find_mount_path(self) -> List[str]:
        """Find the mount path of this device."""
        mount_paths: List[str] = []
        udev_names = self.find_dev_names()
        with open("/proc/mounts", "r") as f:
            for line, udev_name in itertools.product(f, udev_names):
                if udev_name in line:
                    mount_paths.append(line.split()[1])
        return mount_paths
    
    def is_fs_empty(self) -> bool:
        """Check if the filesystem of this device is empty."""
        udev_names = self.find_dev_names()
        if len(udev_names) == 0:
            logger.warning(f"No path found for device '{self}'.")
            sys.exit(1)
        
        # If there is more than one partition, the filesystem is not empty
        if len(udev_names) > 1:
            return False

        mount_paths = self.find_mount_path()
        if len(mount_paths) == 0:
            logger.critical(f"No mount path found for device '{self}'. Please mount it first.")
            sys.exit(1)

        for mount_path in mount_paths:
            if os.listdir(mount_path):
                return False

        return True
    
    def format_device(self, filesystem: str = "ext4", mount_path: Optional[str] = None):
        """Format the device using the provided filesystem."""
        # First, we unmount all partitions
        udev_name = self.find_dev_name()
        for partition_path in self.find_dev_names():
            run_subprocess(f"umount {partition_path}")
        
        # Wiping all partitions
        logger.info(f"Wiping all partitions on the device '{udev_name}'.")
        run_subprocess(f"wipefs --all {udev_name}")

        # Running fdisk to create a new partition
        logger.info(f"Creating a new partition on the device '{udev_name}'.")
        run_subprocess(f"fdisk {udev_name}", input="o\ng\nn\n\n\n\nw\n")

        # Format the partition using filesystem type
        logger.info(f"Creating a new filesystem {filesystem} type on the device.")
        run_subprocess(f"mkfs.{filesystem} {udev_name}1")

        mount_path = input_challenge(
            prompt="Please enter the mount path of the device : ",
            expected_type=str
        )

        # Finally, we mount our new partition
        if not os.path.exists(mount_path):
            os.mkdir(mount_path)
        run_subprocess(f"mount {udev_name} {mount_path}")

    def install_raspbian(self):
        """Install Raspbian OS on the device."""
        def get_latest_raspbian_url():
            url = "https://downloads.raspberrypi.com/raspios_lite_armhf/images/"
            response = requests.get(url)
            if response.status_code != 200:
                logger.critical("Failed to fetch the Raspbian URL on download archives.")
                sys.exit(1)

            body = response.text
            dates = re.findall(r"raspios_lite_armhf-(\d{4}-\d{2}-\d{2})", body, flags=re.MULTILINE)
            if len(dates) == 0:
                logger.critical("Failed to fetch the Raspbian URL on download archives : dates not found.")
                sys.exit(1)
            current_date = datetime(year=2000, month=1, day=1)
            for d in dates:
                current_date = max(current_date, datetime.strptime(d, "%Y-%m-%d"))

            current_date_formatted = current_date.strftime("%Y-%m-%d")
            return f"{url}raspios_lite_armhf-{current_date_formatted}/{current_date_formatted}-raspios-bookworm-armhf-lite.img.xz"

        raspbian_url = get_latest_raspbian_url()
        raspbian_archive = raspbian_url.split("/")[-1]
        raspbian_filename = re.sub(r"\.xz$", "", raspbian_archive)

        if os.path.exists(f".images/{raspbian_filename}"):
            logger.info(f"Found most recent Raspbian OS '{raspbian_filename}'.")
        else:
            logger.info(f"Downloading Raspbian from '{raspbian_url}' locally.")
            run_subprocess(f"curl -o .images/{raspbian_archive} {raspbian_url}")
            logger.info(f"Decompressing Raspbian archive.")
            run_subprocess(f"xz --decompress .images/{raspbian_archive}")
            os.remove(f".images/{raspbian_archive}")

        udev_name = self.find_dev_name()
        logger.info(f"Copying Raspbian image to '{udev_name}'.")
        run_subprocess(f"dd if=.images/{raspbian_filename} of={udev_name} bs=4M status=progress conv=fsync", streaming=True)
        logger.info("Raspbian installation complete.")