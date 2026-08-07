from common.enumerators.device_type import DeviceType
from common.utilities.configuration import Configuration


class NetworkDevice:
    def __init__(self, device_key: str):
        device_details = Configuration.get("NetworkDevices", device_key)

        if device_details is None:
            raise Exception(f"Device {device_key} not found in configuration")

    def connect(self) -> bool:
        raise NotImplementedError("Dev: implement `connect()`")

    def disconnect(self) -> bool:
        raise NotImplementedError("Dev: implement `disconnect()`")

    def verify_name(self, name: str):
        raise NotImplementedError("Dev: implement `verify_name()`")
