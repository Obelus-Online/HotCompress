import yaml


class HotCompressConfiguration:

    def __init__(self):
        with open('config.yaml', 'r') as config_file:
            self.configuration = yaml.safe_load(config_file)

    def get_db_config(self):
        return self.configuration['db']

    def get_compression_config(self):
        return self.configuration['compression']

