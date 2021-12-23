import json
import requests
import sys
import logging
from bson import ObjectId
from mongo_handler.MongoHandler import MongoHandler


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

mongo_handler = MongoHandler()
print(__name__, id(mongo_handler))
headers = {
        'accept': 'application/json',
    }

swimmers = mongo_handler.find_many_docs(col="members", query={"reg_id": {"$ne": "null"}, "firstname": "Dominic"})
for swimmer in swimmers:
    params = (
        ('first_name', swimmers[0]["firstname"]),
        ('last_name', swimmers[0]["lastname"]),
        ('birth', swimmers[0]["birth"]),
        ('reg_id', swimmers[0]["reg_id"]),
    )
    response = requests.post('http://localhost:8000/api/v1/admin', headers=headers, params=params)
    swimmer_records = response.json()["message"]
    # manipulate records 4 testing
    swimmer_records["sc"][0]["50F"]["time"] = "0:22,0"
    update_query = {"$set": {"results": {"records": swimmer_records}}}
    modified_count = mongo_handler.update_one_doc(col="members", _filter={"_id": ObjectId(swimmer["_id"])}, query=update_query)
    print(modified_count)
    break
