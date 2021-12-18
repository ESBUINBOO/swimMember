import hashlib
import requests
import traceback
import os
from subprocess import Popen, PIPE


def check_file_type(file: bytes) -> tuple:
    if isinstance(file, bytes):
        b_file_type = Popen("/usr/bin/file -b --mime -",
                            shell=True, stdout=PIPE, stdin=PIPE).communicate(file[:1024])[0].strip()
        s_file_type = b_file_type.decode('ascii').split()[0].split("/")[1][:-1]
        return b_file_type.decode("utf-8"), s_file_type
    else:
        return ()


def file_is_processable(file_type: str) -> bool:
    # this should be in settings / config
    allowed_file_types = ["png", "jpg", "jpeg", "tif", "tiff", "pdf", "dsv6"]
    rc = False
    if file_type in allowed_file_types:
        rc = True
    return rc


class ConfigHandler(object):
    """
    this class gets the config from ENV-Vars or config.ini
    """
    def __init__(self):
        pass


def get_md5sum_to_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
