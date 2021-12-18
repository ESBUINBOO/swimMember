import pymongo
import logging
import os
import sys

from datetime import datetime
import time
sys.path.append("app")


# this should be done via Logging Config
# copy the ELK Logger from itsc

class SystemLogHandler(logging.Handler):
    """
    Customized logging handler that puts logs to mongo database
    """
    def __init__(self):
        logging.Handler.__init__(self)
        if config['containerized'] == 'False':
            self.host = config['host'] + ':' + config['mongodb_start_port']
            self.mongodb_name = config['mongodb_name']
            self.mongodb_user = config['mongodb_user']
            self.mongodb_pwd = config['mongodb_pwd']
        else:
            self.host = os.getenv('HOST') + ':' + str(os.getenv('MONGODB_START_PORT'))
            self.mongodb_name = os.getenv('MONGODB_NAME')
            self.mongodb_user = os.getenv('MONGODB_USER')
            self.mongodb_pwd = os.getenv('MONGODB_PWD')
        self.uri = "mongodb://" + self.mongodb_user + ":" + self.mongodb_pwd + "@" + self.host + "/" + \
                   self.mongodb_name + "?retryWrites=true&w=majority"
        self.log_error_level = 'DEBUG'
        if config['ssl'] == "True":
            self.client = pymongo.MongoClient(self.uri)
        else:
            self.client = pymongo.MongoClient(self.uri)
        self.db = self.client[self.mongodb_name]
        self.logging_collection = self.db['log_system']

    def emit(self, record):
        # Set current time
        # Clear the log message so it can be put to db via sql (escape quotes)
        log_msg = record.msg
        log_level = str(record.levelno)
        log_level_name = str(record.levelname)
        create_date = datetime.now().isoformat()
        created_by = str(record.name)
        query = {'log_message': log_msg,
                 'log_level': log_level,
                 'log_level_name': log_level_name,
                 'created_by': created_by,
                 'create_date': create_date}
        self.logging_collection.insert_one(query)
