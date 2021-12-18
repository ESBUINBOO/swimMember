import configparser
import os


def read_config():
    config_vars = {}
    config = configparser.ConfigParser()
    config_path = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.join(config_path, "config.ini")
    print(__name__, config_file)
    if os.path.exists(config_file):
        config.read(config_file)
        for section in config:
            for key in config[section]:
                config_vars[key.upper()] = config[section][key]
        return config_vars
    else:
        print('config.ini not found!')
        return


CONFIGS = read_config()