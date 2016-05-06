#encoding=utf-8
import os
from datetime import datetime
import time
import shutil

os.chdir("/search/odin/ftp_data")
#os.chdir("../ftp_data/")
for d in os.listdir("."):
    if os.path.isfile(d):
        t = d.split(".")[0]
        year_month = t[0:6]
        year_month_day = t[0:8]
        year_month_day_hour = t[0:10]
        path =year_month + "/" + year_month_day + "/" + year_month_day_hour + "/"
        os.makedirs(path,exist_ok=True)
        shutil.move(d,path+"/"+d)
