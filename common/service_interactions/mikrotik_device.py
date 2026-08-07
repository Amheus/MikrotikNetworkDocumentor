import routeros_api

from common.utilities.configuration import Configuration
from common.superclasses.network_device import NetworkDevice


class MikrotikDevice(NetworkDevice):
    def __init__(self, device_key: str):
        super().__init__(device_key)

        device_details = Configuration.get("NetworkDevices", device_key)
        connection_details = device_details["Connection"]

        self.connection = routeros_api.RouterOsApiPool(
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

        self.api = None

    def connect(self) -> bool:
        self.api = self.connection.get_api()
        return self.api is not None

    def disconnect(self) -> bool:
        self.connection.disconnect()
        self.api = None
        return True

    def verify_name(self, name: str) -> bool:
        if self.api is None:
            return False

        identities = self.api.get_resource("/system/identity").get()

        if not identities:
            return False

        return identities[0].get("name") == name
