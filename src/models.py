import pyudev
import itertools

from typing import Optional, List

class USBDevice:
    def __init__(self, vendor_id: int, product_id: int, manufacturer_id: Optional[str] = None):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.manufacturer_id = manufacturer_id

        self.name: Optional[str] = None
        self.manufacturer_name: Optional[str] = None

    def __repr__(self):
        return f"{self.name} ({self.manufacturer_name}) - {self.vendor_id:04x}:{self.product_id:04x}"
    
    def find_dev_names(self) -> List[str]:
        """Find the dev names (/dev/sda1, /dev/sda2, ...) associated to this device."""
        udev_names: List[str] = []
        for udev in pyudev.Context().list_devices(subsystem='block', DEVTYPE='partition'):
            found_vendor_id: Optional[int] = udev.get('ID_VENDOR_ID')
            found_model_id: Optional[int] = udev.get('ID_MODEL_ID')
            if found_vendor_id is not None and int(found_vendor_id) == int(f"{self.vendor_id:04x}") \
                and found_model_id is not None and int(found_model_id) == int(f"{self.product_id:04x}"):
                udev_names.append(udev.get('DEVNAME'))
        return udev_names
    
    def find_mount_path(self) -> List[str]:
        """Find the mount path of this device."""
        mount_paths: List[str] = []
        udev_names = self.find_dev_names()
        with open("/proc/mounts", "r") as f:
            for line, udev_name in itertools.product(f, udev_names):
                if udev_name in line:
                    print(line)
                    mount_paths.append(line.split()[1])
        return mount_paths