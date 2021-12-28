import json
import requests
import sys
import logging
from enum import Enum
import dataclasses
from bson import ObjectId
from dataclasses import asdict, is_dataclass, fields
from mongo_handler.MongoHandler import MongoHandler
from dsv6_handler.Dsv6Handler import Dsv6FileHandler
from helper.utils import get_md5sum_to_file
from dsv6_handler.dsv6_data_classes import *

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

mongo_handler = MongoHandler()
logger.info("{} - {}".format(__name__, id(mongo_handler)))
dsv_handler = Dsv6FileHandler()
dsv_handler.update()


def proceed_dsv6_file(dsv_file: str, obj_id=None):
    # todo: das müsste ein update auf ein meetings Document sein, da das Meeting über die GUI angelegt wird
    #  um die Meldungen machen zu können
    logger.info("processing dsv_file {}".format(dsv_file))
    file_hash = get_md5sum_to_file(dsv_file)
    found_doc = mongo_handler.find_one_doc(col="meetings", query={"file_hash": file_hash})
    if found_doc is None:
        results = dsv_handler.analyze_dsv6_file_type(file_to_proceed=dsv_file)
        if list(results.keys())[0] is dsv_handler.return_def[0]:
            print("its a meeting definition")
            meeting = {}
            for k, v in list(results.values())[0].items():
                # print("k: {} - v: {}".format(k, v))
                if isinstance(v, list):
                    meeting[k] = []
                    for item in v:
                        meeting[k].append(item)
                else:
                    # todo: ENUM dataclasses which are fields, wont be casted to dict (its empty),
                    #  so I need to check if the field is enum and set the correct value
                    # for field in fields(v):
                    #     if field.type is Bahnlaenge:
                    #         v.bahnlaenge = v.bahnlaenge.value
                    #         break
                    #     elif field.type is ZeitMessung:
                    #         v.zeitmessung = v.zeitmessung.value
                    #         break
                    #     elif field.type is Geschlecht:
                    #         v.geschlecht = v.geschlecht.value
                    #         break
                    #     elif field.type is Ausuebung:
                    #         v.ausuebung = v.ausuebung.value
                    #         break
                    # print(k, asdict(v))
                    # print("k: {} - v: {}".format(k, v))
                    meeting[k] = v
            obj = {"meeting_definition": meeting, "file_hash": [file_hash]}
            doc_id = mongo_handler.insert_doc(col="meetings", query=obj)
            return doc_id
        elif list(results.keys())[0] is dsv_handler.return_def[1]:
            print("its a meeting result")
            if obj_id is None:
                return False, "No mongo id given"
            results["meeting_results"].pop("meta", None)
            query = {"$set": {"results": results}, "$addToSet": {"file_hash": file_hash}}
            # _filter = {'meeting_definition.Veranstaltung.veranstaltungs_beschreibung': meta["veranstaltungs_beschreibung"]}
            _filter = {"_id": ObjectId(obj_id)}
            logger.debug(query)
            logger.debug(_filter)
            doc_id = mongo_handler.update_one_doc(col="meetings",
                                                  _filter=_filter,
                                                  query=query)
            print(doc_id.modified_count)
            if doc_id.modified_count == 0:
                logger.info("No competition found for this result file")
            return doc_id
    else:
        logger.info("File already processed with hash {}!".format(file_hash))
        return False, "File already processed with hash {}!".format(file_hash)
