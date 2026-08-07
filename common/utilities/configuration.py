
import yaml


class Configuration:

    _CONFIG_ = None

    @staticmethod
    def load(file_path: str):
        with open(file_path, 'r') as file:
            Configuration._CONFIG_ = yaml.safe_load(file)

    @staticmethod
    def get(*path: str):
        temp = Configuration._CONFIG_
        for key in path:
            temp = temp[key]
        return temp

