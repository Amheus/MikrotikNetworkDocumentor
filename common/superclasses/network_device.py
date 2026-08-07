from common.enumerators.device_type import DeviceType
from common.utilities.configuration import Configuration


class NetworkDevice:

    DEVICE_CONFIG: dict|None = None

    def __init__(self, device_key: str):
        self.DEVICE_CONFIG = Configuration.get("NetworkDevices", device_key)

        if self.DEVICE_CONFIG is None:
            raise Exception(f"Device {device_key} not found in configuration")

    def connect(self) -> bool:
        raise NotImplementedError("Dev: implement `connect()`")

    def disconnect(self) -> bool:
        raise NotImplementedError("Dev: implement `disconnect()`")

    def verify_name(self, name: str):
        raise NotImplementedError("Dev: implement `verify_name()`")
