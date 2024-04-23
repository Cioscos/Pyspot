from typing import Optional

import yaml


class ConfigReader:
    """
    A centralized class to read configuration values from a YAML file.

    Attributes:
        config_data (dict): A dictionary to store configuration data loaded from a YAML file.

    Methods:
        __init__(self, config_file): Constructs a ConfigReader instance and loads the configuration data.
        get_config_value(self, key): Retrieves the configuration value for the specified key.
    """

    def __init__(self, config_file):
        """
        Initializes a ConfigReader instance and loads configuration data from the specified YAML file.

        Parameters:
            config_file (str): The path to the YAML configuration file.
        """
        with open(config_file, 'r') as file:
            self.config_data = yaml.safe_load(file)

    def get_config_value(self, key: str) -> Optional[str]:
        """
        Retrieves the configuration value associated with the specified key, supporting nested keys.

        Parameters:
            key (str): The dot-separated key string for the configuration value to be retrieved.

        Returns:
            The configuration value associated with the specified key or nested keys. Returns None if the key does not exist.
        """
        keys = key.split('.')
        value = self.config_data
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            # KeyError is raised if a key is not found.
            # TypeError is raised if an attempt is made to index a non-dict type (e.g., accessing a key on a list or a string).
            return None
