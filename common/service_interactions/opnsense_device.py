from xml.dom.minidom import Element
from xml.etree import ElementTree

from opn_api.api.client import OPNAPIClient, OPNsenseClientConfig
from opn_api.api.core.configbackup import Backup
from opn_api.client import OPNFirewallClient

from common.utilities.configuration import Configuration
from common.superclasses.network_device import NetworkDevice


class OPNSenseDevice(NetworkDevice):
    def __init__(self, device_key: str):
        super().__init__(device_key)

        device_details = Configuration.get("NetworkDevices",  device_key)

        connection_details = device_details["Connection"]

        self._CONNECTION_ = OPNsenseClientConfig(
            api_key=connection_details["ApiKey"],
            api_secret=connection_details["ApiSecret"],
            base_url=connection_details["BaseUrl"],
            ssl_verify_cert=connection_details["SslVerifyCert"]
        )

        self._API_: OPNAPIClient | None = None
        self._CLIENT_: OPNFirewallClient | None = None
        self._CONFIGURATION_: Element|None = None

    @property
    def is_connected(self) -> bool:
        return (
            self._API_ is not None
            and self._CLIENT_ is not None
        )

    def connect(self) -> bool:
        self._API_ = OPNAPIClient(self._CONNECTION_)
        self._CLIENT_ = OPNFirewallClient(self._API_)

        try:
            self._API_.execute(
                module="core",
                controller="system",
                command="status",
                method="get"
            )
        except Exception:
            self._API_ = None
            self._CLIENT_ = None
            return False

        return True

    def disconnect(self) -> bool:
        self._CONFIGURATION_ = None
        self._CLIENT_ = None
        self._API_ = None

        return True

    def get_configuration(
            self,
            refresh: bool = False
    ) -> Element | None:
        if self._API_ is None:
            raise RuntimeError("OPNsense device is not connected")

        if self._CONFIGURATION_ is None or refresh:
            backup = Backup(self._API_)
            configuration = backup.download("this")

            self._CONFIGURATION_ = ElementTree.fromstring(configuration)

        return self._CONFIGURATION_

    def verify_name(self, name: str) -> bool:
        root = self.get_configuration()

        hostname = root.findtext("./system/hostname")

        return hostname == name

