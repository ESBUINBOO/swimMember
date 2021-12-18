import datetime
import logging
import sys
import re
from collections import Counter
# from preprocessing_pipeline import get_data_from_csv
import configparser
import pymongo
from bson.objectid import ObjectId
import json
import os
import uuid
import time
import hashlib
import re
sys.path.append("app")


logger = logging.getLogger('SM_DB_LOGGER')


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return get_instance


@singleton
class MongoHandler(object):
    def __init__(self, uri, db_name):
        try:
            self.uri = uri
            self.db_name = db_name
            self.client = pymongo.MongoClient(self.uri)
            self.db = self.client[self.db_name]
        except Exception as err:
            logger.fatal(err)

    @staticmethod
    def convert_mongodb_cursor_to_list(cursor):
        result_list = []
        for doc in cursor:
            result_obj = {}
            try:
                for k, v in doc.items():
                    # if k == "_id":
                    if type(v) == ObjectId:
                        result_obj[k] = str(v)
                        continue
                    result_obj[k] = v
                result_list.append(result_obj)
            except Exception as e:
                print(e)
        return result_list

    def insert_doc(self, col, query):
        """
        Insert a given document in a given collection
        :param query:
        :param col:
        :return:
        """
        try:
            doc_id = self.db[col].insert_one(query).inserted_id
            return doc_id
        except Exception as err:
            logger.error("Error in insert_doc(): {}".format(str(err)))

    def delete_doc(self, col, query):
        """

        :param col:
        :param query:
        :return:
        """
        try:
            self.db[col].delete_one(filter=query)
        except Exception as err:
            logger.error("Error in delete_doc(): {}".format(str(err)))

    def find_one_doc(self, col, query):
        """
        finds a document in a given collection with a given query
        it returns the document without the ObjectId _id
        :param col:
        :param query:
        :return: document
        :rtype: dict
        """
        try:
            doc = self.db[col].find_one(query)
            if doc is not None:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as err:
            logger.error("Error in find_one_doc(): {}".format(str(err)))

    def find_many_docs(self, col, query, limit=50):
        """
        finds documents in a given collection with a given query
        :param col:
        :param query:
        :param limit:
        :return: list of documents where _id is a string, not an ObjectId
        :rtype: list
        """
        try:
            # todo: regex => Groß- und Kleinschreibung sollte egal sein bsp: regx = re.compile("^foo", re.IGNORECASE)
            docs = self.db[col].find(query).limit(limit)
            return self.convert_mongodb_cursor_to_list(docs)
        except Exception as err:
            logger.error("Error in find_many_docs(): {}".format(str(err)))

    def update_one_doc(self, col, _filter, query):
        """

        :param col:
        :param query:
        :param _filter:
        :return:
        """
        try:
            result = self.db[col].update_one(filter=_filter, update=query, upsert=False)
            return result
        except Exception as err:
            logger.error("Error in update_one_doc(): {}".format(str(err)))
