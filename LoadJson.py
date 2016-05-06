#encoding=utf-8
import json
import os,sys
import codecs
from pprint import pprint

fp = codecs.open("./response.json","r","utf-8")
responses = json.load(fp)
fp.close()

fp = codecs.open("./response.json","w","utf-8")
json.dump(responses,fp,ensure_ascii=False,indent=4)
fp.close()