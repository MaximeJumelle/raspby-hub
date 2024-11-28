import sys




from src.logging import logger

from src.utils import input_challenge
from src.models import USBDevice


def install_raspbian():
    """Install Raspbian OS with utility tools and packages on a device."""
    usb_devices_list = USBDevice.list_devices(require_dev_name=True)
    if len(usb_devices_list) == 0:
        logger.critical("There are no USB device which can be mounted later.")
        sys.exit(1)

    print("\nThe following USB devices were found.\n")
    for i, device in enumerate(usb_devices_list):
        print(f"* [{i + 1}] {device} - {device.find_dev_name()}")

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
    
def setup_raspbian():
    """Configure the Raspberry Pi for first boot."""
    logger.info("Configuring the Raspberry Pi for first boot...")
    usb_devices_list = USBDevice.list_devices(require_dev_name=True)
    if len(usb_devices_list) == 0:
        logger.critical("There are no USB device which can be mounted later.")
        sys.exit(1)

    print("\nThe following USB devices were found.\n")
    for i, device in enumerate(usb_devices_list):
        print(f"* [{i + 1}] {device} - {device.find_dev_name()}")

    print()
    choice = input_challenge(
        prompt="Please select the device where Raspbian is installed : ",
        expected_type=int,
        validator=lambda x: 1 <= x <= len(usb_devices_list)
    )

    selected_device = usb_devices_list[choice - 1]
    mount_paths = selected_device.find_mount_path()

    print("\nThe following mount paths were found.\n")
    for i, path in enumerate(mount_paths):
        print(f"* [{i + 1}] {path}")

    print()
    choice = input_challenge(
        prompt="Please select the mount folder of the boot disk : ",
        expected_type=int,
        validator=lambda x: 1 <= x <= len(mount_paths)
    )

    boot_path = mount_paths[choice - 1]
    if input_challenge(
        prompt="Do you want to enable SSH ? (yes/no): ",
        expected_type=str,
        validator=lambda x: x.lower() in ["yes", "no"]
    ).lower() == "yes":
        ssh_file_path = f"{boot_path}/ssh"
        with open(ssh_file_path, 'w') as ssh_file:
            ssh_file.write("")
        logger.info("SSH has been enabled.")
        pass


    if input_challenge(
        prompt="Do you want to configure Wi-Fi connection ? (yes/no): ",
        expected_type=str,
        validator=lambda x: x.lower() in ["yes", "no"]
    ).lower() == "yes":
        pass
    