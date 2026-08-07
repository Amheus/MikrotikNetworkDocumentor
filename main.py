from common.enumerators.device_type import DeviceType
from common.utilities.configuration import Configuration
from common.service_interactions.mikrotik_device import MikrotikDevice
from common.superclasses.network_device import NetworkDevice


def main() -> None:
    Configuration.load("config.yaml")

    devices_config = Configuration.get("NetworkDevices")

    network: list[NetworkDevice] = []

    print("Connecting to devices...")

    try:
        for device_name, device_details in devices_config.items():
            device_type = device_details["Type"]

            if device_type == DeviceType.MikroTIK.value:
                device = MikrotikDevice(device_name)
            else:
                print(f"    {device_name} - UNSUPPORTED ({device_type})")
                continue

            print(f"    {device_name}", end="")

            if not device.connect():
                raise RuntimeError(f"Failed to connect to {device_name}")

            if not device.verify_name(device_name):
                device.disconnect()
                raise RuntimeError(f"Device {device_name} is not the expected device")

            network.append(device)

            print(" - CONNECTED")

    finally:
        print("Disconnecting from devices...")

        for device in network:
            device.disconnect()

        print("Done :3")


if __name__ == "__main__":
    main()
