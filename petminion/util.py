import platformdirs
import configparser
import logging
import os

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


class AppConfig:
    """Provides read/write access to application config file"""

    def __init__(self):
        self.filename = filename = os.path.join(
            user_config_dir(), "config.ini")
        logger.info(
            "Reading application settings from {filename} - you can edit this file to change options.")
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
        # FIXME - someday if this class is reused, move this default stuff elsewhere
        self.config['DEFAULT'] = {
            'MQTTHost': 'localhost',
            'Feeder': 'ZigbeeFeeder',
            'TrainingRule': 'SimpleFeederRule'
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
