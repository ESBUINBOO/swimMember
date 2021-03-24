from fastapi import APIRouter, UploadFile, File
import os
from selenium_handler.selenium_handler import SeleniumHandler
from bs4_handler.bs4_handler import beautify_results

router = APIRouter()
url = "https://dsvdaten.dsv.de/Modules/Results/Individual.aspx?Lang=de-DE"  # todo: in die config.ini schieben
selenium_handler_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'selenium_handler'))
selenium_handler = SeleniumHandler(url=url, driver_path=os.path.join(selenium_handler_path, "drivers/chromedriver_mac"))


@router.post("/api/v1/admin/swimmer/records/",
             include_in_schema=True,
             description="Start selenium process to fetch swimmers all time records")
async def update_admin(first_name: str, last_name: str, birth: str, reg_id: int):
    raw_html = selenium_handler.get_info(first_name=first_name, last_name=last_name, birth=birth,
                                         dsv_id=str(reg_id))
    result = beautify_results(raw_html)

    return {"message": result}


@router.post("/api/v1/upload/")
async def upload_file(file: UploadFile = File(...)):
    if not os.path.exists("files"):
        os.mkdir("files")
    file_name = os.getcwd() + "/files/" + file.filename.replace(" ", "-")
    with open(file_name, 'wb+') as f:
        f.write(file.file.read())
        f.close()
    return {"message": file.filename}
