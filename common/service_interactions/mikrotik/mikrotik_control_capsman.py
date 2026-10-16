from common.service_interactions.mikrotik_device import MikrotikDevice


class MikrotikControlCapsman:
    def __init__(self, mikrotik_device: MikrotikDevice):
        if not isinstance(mikrotik_device, MikrotikDevice):
            raise TypeError(
                "mikrotik_device must be of type MikrotikDevice"
            )

        self._DEVICE_ = mikrotik_device

    def get_provisioning_data(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/caps-man/provisioning")

    def get_configuration_data(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/caps-man/configuration")

    def get_channel_data(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/caps-man/channel")

    def get_security_data(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/caps-man/security")

    def get_datapath_data(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/caps-man/datapath")

    def get_interface_data(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/caps-man/interface")

    def get_registration_table(self) -> list[dict]:
        return self._DEVICE_.get_resource_data("/caps-man/registration-table")

    def build_payload(self) -> dict:
        configurations = self.get_configuration_data()
        channels = self.get_channel_data()
        data_paths = self.get_datapath_data()
        securities = self.get_security_data()

        channels_by_name = {
            channel["name"]: channel
            for channel in channels
            if "name" in channel
        }

        data_paths_by_name = {
            data_path["name"]: data_path
            for data_path in data_paths
            if "name" in data_path
        }

        securities_by_name = {
            security["name"]: security
            for security in securities
            if "name" in security
        }

        builder = {
            "configurations": {},
            "provisioningRules": [],
        }

        for config in configurations:
            name = config["name"]

            channel_name = config.get("channel")
            data_path_name = config.get("datapath")
            security_name = config.get("security")

            channel = channels_by_name.get(channel_name, {})
            data_path = data_paths_by_name.get(data_path_name, {})
            security = securities_by_name.get(security_name, {})

            builder["configurations"][name] = {
                "country": config.get("country"),
                "distance": config.get("distance"),
                "installation": config.get("installation"),
                "mode": config.get("mode"),
                "ssid": config.get("ssid"),

                "channel": {
                    "name": channel_name,
                    "band": channel.get("band"),
                    "controlChannelWidth": channel.get("control-channel-width"),
                    "frequency": channel.get("frequency"),
                },

                "dataPath": {
                    "name": data_path_name,
                    "clientToClientForwarding": data_path.get(
                        "client-to-client-forwarding"
                    ),
                    "localForwarding": data_path.get(
                        "local-forwarding"
                    ),
                    "vlanId": data_path.get("vlan-id"),
                    "vlanMode": data_path.get("vlan-mode"),
                },

                "security": {
                    "name": security_name,
                    "authenticationType": security.get(
                        "authentication-types"
                    ),
                    "encryption": security.get("encryption"),
                    "password": "[REDACTED]",
                },
            }

        for order, rule in enumerate(self.get_provisioning_data()):
            builder["provisioningRules"].append({
                "enabled": rule.get("disabled") != "true",
                "order": order,
                "comment": rule.get("comment"),
                "match": {
                    "hardwareSupportedModes": rule.get("hw-supported-modes", []),
                    "identityRegex": rule.get("identity-regexp"),
                    "commonNameRegex": rule.get("common-name-regexp"),
                    "ipAddressRanges": rule.get("ip-address-ranges"),
                    "radioMac": rule.get("radio-mac"),
                },
                "action": rule.get("action"),
                "masterConfiguration": rule.get( "master-configuration"),
                "slaveConfigurations": rule.get("slave-configurations", []),
                "interfaceNaming": {
                    "format": rule.get("name-format"),
                    "namePrefix": rule.get("name-prefix"),
                },
            })

        return builder