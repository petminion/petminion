import configparser
import logging
import os

import jsonpickle
import platformdirs

app_name = "petminion"
app_author = "geeksville"
logger = logging.getLogger()


def user_data_dir():
    """Get our data directory"""
    return platformdirs.user_data_dir(app_name, app_author, ensure_exists=True)


def user_cache_dir():
    """Get our cache directory"""
    return platformdirs.user_cache_dir(app_name, app_author, ensure_exists=True)


def user_config_dir():
    """Get our config directory"""
    return platformdirs.user_config_dir(app_name, app_author, ensure_exists=True)


def user_state_dir():
    """Get our state directory"""
    return platformdirs.user_state_dir(app_name, app_author, ensure_exists=True)


def save_state(file_base_name: str, data: any) -> None:
    """Save an object's state using jsonpickle"""
    path = os.path.join(user_state_dir(), file_base_name + ".json")
    logger.debug(f'Saving state to {path}')
    json = jsonpickle.encode(data, indent=2)
    with open(path, "w") as f:
        f.write(json)


def load_state(file_base_name: str, default_value: any = None) -> any:
    """
    Load an object's state using jsonpickle.

    Args:
        file_base_name (str): The base name of the file to load the state from.
        default_value (any, optional): The default value to return if loading the state fails. Defaults to None.

    Returns:
        any: The loaded object's state.

    Raises:
        Exception: If loading the state fails and no default value is provided.
    """
    try:
        path = os.path.join(user_state_dir(), file_base_name + ".json")
        logger.debug(f'Loading state from {path}')
        with open(path, "r") as f:
            json = f.read()
            return jsonpickle.decode(json)
    except Exception as e:
        if default_value:
            logger.warning(f'Failed to load state from {path}, using defaults...')
            return default_value
        else:
            raise e


class AppConfig:
    """Provides read/write access to application config file"""

    def __init__(self):
        """
        Initializes an instance of MyClass.

        This method sets up the filename, logger, and configuration for the class.
        It reads the application settings from the config.ini file and sets defaults if necessary.
        """
        self.filename = filename = os.path.join(
            user_config_dir(), "config.ini")
        logger.info(
            f"Reading application settings from {filename} - you can edit this file to change options.")
        self.config = config = configparser.ConfigParser()

        self.set_defaults()
        config['settings'] = {}
        if not os.path.exists(filename):
            self.save()
        else:
            config.read(filename)
            # always reset the defaults because they might have changed in development
            self.set_defaults()

    def set_defaults(self):
        """
        Sets the default configuration values for the PetMinion class.

        This method initializes the 'DEFAULT' section of the configuration dictionary
        with default values for various settings such as 'MQTTHost', 'Feeder', 'Camera',
        'TrainingRule', 'FastModel', and 'SimFallback'.

        Note:
            If this class is reused in the future, it is recommended to move the default
            configuration values to a separate location.

        """
        self.config['DEFAULT'] = {
            'MQTTHost': 'localhost',
            'Feeder': 'ZigbeeFeeder',
            'Camera': 'CV2Camera',
            'TrainingRule': 'SimpleFeederRule',
            'FastModel': False,
            'SimFallback': True,
            'SimSocialMedia': False
        }

    @property
    def settings(self):
        """Return the first customized set of settings"""
        return self.config['settings']

    def save(self):
        """Store a (possibly modified config) to the filesystem"""
        with open(self.filename, 'w') as f:
            self.config.write(f)


app_config = AppConfig()
