from xml.etree import ElementTree

from common.service_interactions.opnsense_device import OPNSenseDevice


class OpnsenseControlVlan:
    def __init__(self, opnsense_device: OPNSenseDevice):
        if not isinstance(opnsense_device, OPNSenseDevice):
            raise TypeError("opnsense_device must be of type OPNSenseDevice")

        self._DEVICE_ = opnsense_device

    def build_payload(self) -> list[dict]:
        configuration = self._DEVICE_.get_configuration()

        vlans = []

        for vlan in configuration.findall("./vlans/vlan"):
            vlans.append({
                "interface": vlan.findtext("if"),
                "tag": self._to_int(vlan.findtext("tag")),
                "priority": self._to_int(vlan.findtext("pcp")),
                "protocol": vlan.findtext("proto"),
                "description": vlan.findtext("descr"),
                "device": vlan.findtext("vlanif"),
            })

        return vlans

    @staticmethod
    def _to_int(value: str | None) -> int | None:
        if value is None or value == "":
            return None

        return int(value)
