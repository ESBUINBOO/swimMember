import json
import requests
import sys
import logging
from bson import ObjectId
from mongo_handler.MongoHandler import MongoHandler
from dsv6_handler.Dsv6Handler import Dsv6FileHandler
from helper.utils import get_md5sum_to_file

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

mongo_handler = MongoHandler()
logger.info("{} - {}".format(__name__, id(mongo_handler)))
dsv_handler = Dsv6FileHandler()
dsv_handler.update()

for dsv_file in dsv_handler.files_to_proceed.copy():
    # todo: das müsste ein update auf ein meetings Document sein, da das Meeting über die GUI angelegt wird
    #  um die Meldungen machen zu können
    logger.info("processing dsv_file {}".format(dsv_file))
    file_hash = get_md5sum_to_file(dsv_file)
    found_doc = mongo_handler.find_one_doc(col="meetings", query={"file_hash": file_hash})
    if found_doc is None:
        results = dsv_handler.get_results_from_file(file_to_proceed=dsv_file)
        meta = results["meta"]
        results.pop("meta", None)
        obj = {"meta": meta, "results": results, "file_hash": file_hash}
        doc_id = mongo_handler.insert_doc(col="meetings", obj=obj)
    else:
        logger.info("File already processed with hash {}! Skipping this one!".format(file_hash))
