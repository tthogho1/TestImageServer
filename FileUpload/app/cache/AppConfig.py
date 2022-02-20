import configparser
import os
from os import path

class AppConfig:
    _instance = None
    _config_ini = None
    _confpath = "./app/cache/Appconf.ini"

    def __init__(self):
        if self._config_ini == None:
            self._config_ini = configparser.ConfigParser()
            print(os.getcwd())
            if (path.exists(self._confpath)):
                print("read conf file")
                self._config_ini.read(self._confpath)
        pass

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        
        return cls._instance

    
    def get_config(self):
        return self._config_ini
