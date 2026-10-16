from typing import Any

import routeros_api

from common.utilities.configuration import Configuration
from common.superclasses.network_device import NetworkDevice


class MikrotikDevice(NetworkDevice):
    def __init__(self, device_key: str):
        super().__init__(device_key)

        device_details = Configuration.get("NetworkDevices", device_key)
        connection_details = device_details["Connection"]

        self._CONNECTION_ = routeros_api.RouterOsApiPool(
            connection_details["IP"],
            username=connection_details["Username"],
            password=connection_details["Password"],
            port=connection_details["Port"],
            plaintext_login=connection_details["PlaintextLogin"],
            use_ssl=connection_details["UseSsl"],
            ssl_verify=connection_details["SslVerify"],
            ssl_verify_hostname=connection_details["SslVerifyHostname"],
            ssl_context=connection_details["SslContext"],
        )

        self._API_ = None

    @property
    def is_connected(self) -> bool:
        return self._API_ is not None

    def connect(self) -> bool:
        self._API_ = self._CONNECTION_.get_api()
        return self._API_ is not None

    def disconnect(self) -> bool:
        self._CONNECTION_.disconnect()
        self._API_ = None
        return True

    def get_resource(self, path: str) -> Any:
        if self._API_ is None:
            raise RuntimeError("MikroTik device is not connected")

        return self._API_.get_resource(path)

    def get_resource_data(self, path: str, **filters) -> list[dict]:
        return self.get_resource(path).get(**filters)

    def verify_name(self, name: str) -> bool:
        identities = self.get_resource_data("/system/identity")

        if not identities:
            return False

        return identities[0].get("name") == name
