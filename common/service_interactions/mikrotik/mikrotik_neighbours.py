import json
from xml.etree import ElementTree

from common.service_interactions.mikrotik_device import MikrotikDevice


class MikrotikNeighbours:
    def __init__(self, mikrotik_device: MikrotikDevice):
        if not isinstance(mikrotik_device, MikrotikDevice):
            raise TypeError(
                "mikrotik_device must be of type MikrotikDevice"
            )

        self._DEVICE_ = mikrotik_device

    def build_payload(self) -> dict:
        builder = {
        }
        return builder

    @staticmethod
    def _to_int(value: str | None) -> int | None:
        if value is None or value == "":
            return None

        return int(value)
