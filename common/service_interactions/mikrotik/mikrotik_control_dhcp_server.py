import json
from xml.etree import ElementTree

from common.service_interactions.mikrotik_device import MikrotikDevice


class MikrotikControlDhcpServer:
    def __init__(self, mikrotik_device: MikrotikDevice):
        if not isinstance(mikrotik_device, MikrotikDevice):
            raise TypeError(
                "mikrotik_device must be of type MikrotikDevice"
            )

        self._DEVICE_ = mikrotik_device

    def get_servers(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/ip/dhcp-server")

    def get_networks(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/ip/dhcp-server/network")

    def get_static_leases(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/ip/dhcp-server/lease", dynamic="no")

    def build_payload(self) -> dict:
        builder = {
            "servers": self.get_servers(),
            "networks": self.get_networks(),
            "staticLeases": self.get_static_leases(),
        }
        return builder

    @staticmethod
    def _to_int(value: str | None) -> int | None:
        if value is None or value == "":
            return None

        return int(value)
