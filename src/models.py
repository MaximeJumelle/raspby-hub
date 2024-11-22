import sys
import re
import os
import pyudev
import itertools

from typing import Optional, List

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
                and found_model_id is not None and str(found_model_id) == f"{self.product_id:04x}":
                return udev.get('DEVNAME')
    
    def find_dev_names(self) -> List[str]:
        """Find the dev names (/dev/sda1, /dev/sda2, ...) associated to this device."""
        udev_names: List[str] = []
        for udev in pyudev.Context().list_devices(subsystem='block', DEVTYPE='partition'):
            found_vendor_id: Optional[int] = udev.get('ID_VENDOR_ID')
            found_model_id: Optional[int] = udev.get('ID_MODEL_ID')
            if found_vendor_id is not None and str(found_vendor_id) == f"{self.vendor_id:04x}" \
                and found_model_id is not None and str(found_model_id) == f"{self.product_id:04x}":
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
        run_subprocess(f"wipefs --all {udev_name}")

        # Running fdisk to create a new partition
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