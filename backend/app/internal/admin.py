import sys
import os
import platform
from typing import List
from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
sys.path.append("app")
from models.models import JsonResponseContent
from helper.utils import check_file_type, file_is_processable
from selenium_handler.selenium_handler import SeleniumHandler
from bs4_handler.bs4_handler import beautify_results

router = APIRouter()
url = "https://dsvdaten.dsv.de/Modules/Results/Individual.aspx?Lang=de-DE"
selenium_handler_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'selenium_handler'))
if platform.system() == "Linux":
    selenium_driver = "drivers/chromedriver_lin"
elif platform.system() == "Darwin":
    selenium_driver = "drivers/chromedriver_mac"
# selenium_handler = SeleniumHandler(url=url, driver_path=os.path.join(selenium_handler_path, selenium_driver))

# content = JsonResponseContent()  # todo: check if everytime the class should be instantiated


@router.post("/api/v1/admin/swimmer/records/",
             include_in_schema=True,
             description="Start selenium process to fetch swimmers all time records")
async def get_records(first_name: str, last_name: str, birth: str, reg_id: int):
    raw_html = selenium_handler.get_info(first_name=first_name, last_name=last_name, birth=birth,
                                         dsv_id=str(reg_id))
    result = beautify_results(raw_html)

    return JSONResponse(status_code=201, content={"result": True, "message": result, "detail": None})


@router.post("/api/v1/upload/")
async def upload_file(files: List[UploadFile] = File(...)):
    # todo: upload this files to S3 Bucket
    # check if files are processable; i think this is not a web-standard way
    # todo: maybe its good to write a FileHandler, to check, upload etc files
    if len(files) == 0:
        return JSONResponse(status_code=400, content={"result": False,
                                                      "message": "Bad Request",
                                                      "detail": "No Files found"})
    contents = [await i.read() for i in files]  # list of bytes
    file_names = [i.filename for i in files]
    files_to_check = dict(zip(file_names, contents))
    not_processable = {}
    for k, v in files_to_check.items():
        file_type = check_file_type(file=v)
        if len(file_type) == 0:  # could not get file types, so lets say we cant process them x)
            not_processable[k] = False
            continue
        if file_is_processable(file_type=file_type[1]) is False:  # index 0 = mime type; index 1 = file typ
            not_processable[k] = False
    if len(not_processable) > 0:
        return JSONResponse(status_code=415, content={"result": False,
                                                      "message": "Unsupported Media Type",
                                                      "detail": "{} of {} could not be processed. Please check file(s) {}".format(
                                                          len(not_processable), len(files),
                                                          list(not_processable.keys()))})

    if not os.path.exists("files"):
        os.mkdir("files")
    for file in files:
        file_name = os.getcwd() + "/files/" + file.filename.replace(" ", "-")
        with open(file_name, 'wb+') as f:
            f.write(file.file.read())
            f.close()
    return JSONResponse(status_code=201,
                        content={"result": True,
                                 "message": "uploaded {} file(s)".format(len(files)),
                                 "detail": None})
