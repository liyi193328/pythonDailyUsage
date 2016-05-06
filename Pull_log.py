#encoding=utf-8
import os,sys
import json
import pickle
import codecs
from pprint import pprint
import urllib.request
import time
from datetime import datetime,timedelta

def ResponseOfurl(url):
    '''
    输入：url
    返回：response或-1
    根据url返回response的str形式，如果请求超时则返回-1
    '''
    try:
        print("url:",url)
        f = urllib.request.urlopen(url)
        response = f.read().decode("utf-8")
        return response
    except ValueError:
        print("valueError url:",url)
        return "-1"
    except:
        import traceback
        traceback.print_exc()
        return "-1"

def ResponseOfurl_to_file(url,out):
    '''
    输入：url，out（绝对路径）
    将请求url返回的response写入到out所指定的文件里面
    '''
    response = ResponseOfurl(url)
    response = str(response)
    if response != "-1":
        with codecs.open(out,"w","utf-8") as f:
            f.write(response)

def ParseUrl(url):
    '''
    输入：解析url
    返回：网站地址，路径和query的参数
    '''
    from urllib.parse import urlparse,urlsplit,parse_qs
    components = urlparse(url)
    query = parse_qs(components.query)
    return [components.netloc,components.path,query]

def Url_Response_Json(url,o_json_file):
    '''
    输入：url，json输出文件
    将url对应的response以json的形式保留在o_json_file里面，添加url和解析url的结果
    '''
    url = url.strip()
    parsed_url = ParseUrl(url)
    if url == "":
        return
    response = ResponseOfurl(url)
    # print("response:",str(response))
    response_json = json.loads(str(response))
    if str(response_json) != "-1":
        response_json['url'] = url
        response_json['parsed_url'] = parsed_url
    f = codecs.open(o_json_file,"w","utf-8")
    json.dump(response_json,f,ensure_ascii=False,indent=4)
    f.close()

def File_Response_Json(inputFilename,outputFilename):
    '''
    将inputFilename中的url（每一行是一个url）的response全部放入到outputFilename中
    '''
    f = codecs.open(inputFilename,"r","utf-8")
    responses = []
    for line in f.readlines():
        url = line.strip()
        if url == "":
            continue
        response = ResponseOfurl(url)
        # print("response:",response)
        response_json = json.loads(str(response))
        if str(response_json) != "-1":
            # print(response_json)
            response_json['url'] = url
            responses.append(response_json)
        # input("xx:")
    f.close()
    f = codecs.open(outputFilename,"w","utf-8")
    json.dump(responses,f,ensure_ascii=False,indent=4)
    f.close()

def TimeLog_Toutiao():
    pass
def time_1min(nowdate):
    '''
    每分钟从给定的网址中下拉log文件，存储本地命名格式为201603141315:2016/03/14/ - 13:15
    '''
    # prefix = "http://101.200.158.230:8888/6393f6914cf892b1a4eec9d5ee5b5bcf/u_ex"
    prefix = "http://www.alphago2016.com:6001/544261cae5a08185c17fda644e8e6e82/u_ex"
    # nowdate = datetime.now()
    year_month = nowdate.strftime("%Y%m")
    year_month_day = nowdate.strftime("%Y%m%d")
    year_month_day_hour = nowdate.strftime("%Y%m%d%H")
    year_month_day_hour_min = nowdate.strftime("%Y%m%d%H%M")
    url_date = year_month_day_hour[2:] ##16031413
    # print(nowdates)
    try_times = 2
    t = 0
    while(t < try_times):
        url = prefix + url_date + ".log"
        try:
            path = "../ftp_data/" + year_month + "/" + year_month_day + "/" + year_month_day_hour + "/" + year_month_day_hour_min+".log"
            os.makedirs(os.path.dirname(path),exist_ok=True)
            ResponseOfurl_to_file(url,path)
            t = try_times
        except:
            import traceback
            traceback.print_exc()
            print("sleep 30...")
            time.sleep(30)
            print("end sleep")
            t += 1
            print("begin to try %s times.."%t)
def time_1min_loop(From,To=None):
    if To == None:
        time_1min(From)
    else:
        while(From <= To):
            time_1min(From)
            From += timedelta(minutes=1)
            print(From,"...")
            time_1min(From)

if __name__ == '__main__':
    # Response2json("./url1.txt","./response_v1.json")
    # response = ResponseOfurl("http://101.200.158.230:8888/6393f6914cf892b1a4eec9d5ee5b5bcf/u_ex16031415.log")
    # with codecs.open("raw.txt","w","utf-8") as f:
    #   f.write(response)
    # url = "http://ic.snssdk.com/2/article/v25/stream/?count=20&min_behot_time=1457672142&bd_city=%E5%8C%97%E4%BA%AC%E5%B8%82&bd_latitude=40.08686&bd_longitude=116.336227&bd_loc_time=1457671953&loc_mode=7&loc_time=1457671306&latitude=40.092552660465&longitude=116.34280131795&city=%E5%8C%97%E4%BA%AC%E5%B8%82&iid=3827265717&device_id=7564326355&ac=wifi&channel=baidu&aid=13&app_name=news_article&version_code=466&device_platform=android&device_type=HM%202A&os_api=19&os_version=4.4.4&uuid=867711021068618&openudid=bd3fc32793ae8854&"
    # Url_Response_Json(url,"test2.json")
    # parsed_url = ParseUrl(url)
    argv = sys.argv
    if len(argv) == 3:
        Froms = argv[1]
        Tos = argv[2]
        From = datetime.strptime(Froms,"%Y%m%d%H%M")
        To = datetime.strptime(Tos,"%Y%m%d%H%M")
        time_1min_loop(From,To)
    elif len(argv) == 1:
        now = datetime.now()
        time_1min_loop(now,None)
    else:
        print("fromat: year_month_day_hour_min year_month_day_hour_min")
        print("or nothing")
