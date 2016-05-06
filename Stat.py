#encoding=utf-8
import os,sys
import json
import pickle
import codecs
from pprint import pprint
import urllib.request
import time
from datetime import datetime,timedelta
import glob
import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='toutiao.log',
    level="DEBUG",
    filemode='w')

def readJson(p):
    fp = codecs.open(p,"r","utf-8")
    return json.load(fp)

def dumpJson(obj,p):
    if type(obj) == set:
        obj=list(obj)
    fp = codecs.open(p,"w","utf-8")
    json.dump(obj,fp,ensure_ascii=False,indent=4)
    fp.close()

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
        print("catch url error:")
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
    for key in query.keys():
        if len(query[key]) > 0:
            query[key] = query[key][0]
    return {"scheme":components.scheme,"netloc":components.netloc,"path":components.path,"query":query}

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

def Log_Url_Parse(path):
    f = codecs.open(path,"r","utf-8")
    parsed_urls = []
    for line in f.readlines():
        if len(line) == 0:
            continue
        line = line.strip()
        if line[0] == '#':continue
        t = line.split(" ")
        if len(t) < 5:continue
        url = t[4][1:]
        if t[5].strip() != "-":
            url += "?"+t[5].strip()
        url = url.replace("http:/","http://")
        # print(url)
        parsed_url = ParseUrl(url)
        if parsed_url['scheme'] != "":
            # print(parsed_url)
            parsed_urls.append(parsed_url)
        # pprint(parsed_url)
        # input("xx:")
    return parsed_urls

def Cal_last_xth_day_Ratio(nowdate,xth,dataLoc,cur_users,IsnewRemain=False):
    '''
    nowdate:给定的当前时间（datetime格式）
    dataLoc:json数据存放位置
    cur_users:当前时间的用户列表（set数据格式）
    IsnewRemain:如果为true，则计算新增用户的留存；否则计算用户留存
    返回：残留率 or -1
    '''
    last_xth_day = nowdate - timedelta(days=xth)
    last_xth_day_str = last_xth_day.strftime("%Y%m%d")
    prefix = "users_"
    if IsnewRemain == True:
        prefix = "new_users_"
    fname = prefix + last_xth_day_str + ".json"
    p = os.path.join(dataLoc,fname)
    if os.path.exists(p) == True:
        fp = codecs.open(p,"r","utf-8")
        last_xth_users = set(json.load(fp))
        remain_users = cur_users.intersection(last_xth_users)
        remain_xth_ratio = float(len(remain_users)) / float(len(last_xth_users))
        return remain_xth_ratio
    return 0.0

def Cal_xth_all_users(nowdate,xth,dataLoc,cur_users):
    '''
    计算xth天前到当前给定时期的所有用户数量，返回数值
    '''
    last_xth_day = nowdate - timedelta(days=xth)
    x = last_xth_day
    y = nowdate
    Ans = {}
    while(x <= y):
        x_str = x.strftime("%Y%m%d")
        fname = "users_" + x_str + ".log"
        p = os.path.join(dataLoc,fname)
        if os.path.exists(p)==True:
            fp = codecs.open(p,"r","utf-8")
            x_users = json.load(fp)
            Ans = Ans.union(x_users)
        x += timedelta(days=1)
    return len(Ans)

def Cal_new_users(nowdate,dataLoc,cur_users,Isstore=True):
    '''
    根据当前用户和历史所有用户(dataLoc/all_users.json)计算新用户数目，存储为new_users_{nowdate}.json
    返回新用户数目
    '''
    p = os.path.join(dataLoc,"all_users.json")
    year_month_day = nowdate.strftime("%Y%m%d")
    new_users = {}
    if os.path.exists(p) == True:
        fp = codecs.open(p,"r","utf-8")
        try:
            all_users = set(json.load(fp))
        except:
            print("all_users.json load error")
            return 0
        fp.close()
        new_users = cur_users.difference(all_users)
        new_p = os.path.join(dataLoc,"new_users_" + year_month_day + ".json")
        dumpJson(new_users,new_p)
        return len(new_users)
    else:
        logging.info("not find " + p)
        print("not find", p)
    return 0

def Store_all_users(nowdate,dataLoc,cur_users):
    '''
    根据合并当前用户和历史所有用户，进行存储
    保留两份：
    {dataLoc}/all_users.json
    {dataLoc}/all_users_{nowdate}.json
    '''
    p = os.path.join(dataLoc,"all_users.json")
    year_month_day = nowdate.strftime("%Y%m%d")
    new_users = {}
    try:
        fp = codecs.open(p,"r","utf-8")
        all_users = set(json.load(fp))
        fp.close()
        all_users = all_users.union(cur_users)
        new_p = os.path.join(dataLoc,"all_users.json")
        dumpJson(all_users,new_p)
        new_p = os.path.join(dataLoc,"all_users_" + year_month_day + ".json")
        dumpJson(all_users,new_p)
        return len(new_users)
    except:
        new_p = os.path.join(dataLoc,"all_users.json")
        dumpJson(cur_users,new_p)
        logging.exception("not find " + new_p)
        import traceback
        traceback.print_exc()
    return -1

def ActionFromUrl(url):
    pass

def Day_Log_Toutiao(From,user_id="uuid",storePath=""):

    gaps = [1,3,7]

    nowdate = From
    year_month = nowdate.strftime("%Y%m")
    year_month_day = nowdate.strftime("%Y%m%d")
    year_month_day_hour = nowdate.strftime("%Y%m%d%H")
    year_month_day_hour_min = nowdate.strftime("%Y%m%d%H%M")
    day_dir_path = "../ftp_data/" +  year_month + "/" + year_month_day + "/"
    day_stat_path = "../stat/"
    # os.chdir(day_dir_path) ##enter /search/odin/ftp_data/201603/20160314
    users_today = set()
    users_today_list = list()
    article_content_cnt = {}
    pull_cnt = {}
    for dirpath,dirnames,filenames in os.walk(day_dir_path):
        for filename in filenames:
            if ".log" not in filename:
                continue
            print(filename)
            log_path = os.path.join(dirpath,filename)
            # logging.info("begin to handle " + log_path + "...")
            parsed_urls = Log_Url_Parse(log_path)
            fp = codecs.open(log_path.replace(".log","_parsed.path"),"w","utf-8")
            json.dump(parsed_urls,fp,ensure_ascii=False,indent=4)
            fp.close()
            # print("len(parsed_urls):",len(parsed_urls))
            for index,parsed_url in enumerate(parsed_urls):
                url_path = parsed_url['path']
                query = parsed_url['query']
                # print("url_path:",url_path)
                user = "-1"
                if user_id in query.keys():
                    user = parsed_url['query'][user_id].strip()
                    users_today.add(user)
                    users_today_list.append(user)
                if 'article' in url_path and 'content' in url_path:
                    if user not in article_content_cnt.keys():
                        article_content_cnt[user] = 1
                    else:
                        article_content_cnt[user] += 1
                if 'all_comments' in url_path:
                    if user not in pull_cnt.keys():
                        pull_cnt[user] = 1
                    else:
                        pull_cnt[user] += 1

    os.makedirs(day_stat_path,exist_ok=True)
    #存储今日用户数据
    usersfile = "users_" + year_month_day + ".json"
    p = os.path.join(day_stat_path,usersfile)
    dumpJson(list(users_today),p)
    print("dump today user to " + p)

    today_users_num = len(users_today)
    print("today has total ",today_users_num," users")
    # stat = {"pull_cnt":pull_cnt,"article_content_cnt":article_content_cnt}
    total_7days_users_num = Cal_xth_all_users(nowdate,7,day_stat_path,users_today)
    ##计算并存储了今日新用户数据
    print("begin to cal today's new users")
    new_users_num = Cal_new_users(nowdate,day_stat_path,users_today,Isstore=True)
    stat = {
    "total_7days_users_num":total_7days_users_num,
    "new_users_num":new_users_num,
    "today_users_num":today_users_num,
    "today_old_users_num":today_users_num - new_users_num
    }
    for gap in gaps:
        print("gap " + str(gap) + "...")
        x = Cal_last_xth_day_Ratio(nowdate,gap,day_stat_path,users_today,IsnewRemain=False)
        key = 'new_users_radio_'+str(gap)
        stat[key] = x 
        y = Cal_last_xth_day_Ratio(nowdate,gap,day_stat_path,users_today,IsnewRemain=False)
        key = "users_radio_"+str(gap)
        stat[key] = y

    #存储统计数据
    statfile = "stat_" + year_month_day+".json"
    p = os.path.join(day_stat_path,statfile)
    print(stat)
    dumpJson(stat,p)
    print("dump stat data to " + p )

    ##合并历史用户数据，并存储
    Store_all_users(nowdate,day_stat_path,users_today)
    print("merge all users data to all_users.json")

def mergeUsers(files,storePath):
    pass
    
def time_1min():
    '''
    每分钟从给定的网址中下拉log文件，存储本地命名格式为201603141315:2016/03/14/ - 13:15
    '''
    # prefix = "http://101.200.158.230:8888/6393f6914cf892b1a4eec9d5ee5b5bcf/u_ex"
    prefix = "http://www.alphago2016.com:6001/544261cae5a08185c17fda644e8e6e82/u_ex"
    nowdate = datetime.now()
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

if __name__ == '__main__':
    # Response2json("./url1.txt","./response_v1.json")
    # response = ResponseOfurl("http://101.200.158.230:8888/6393f6914cf892b1a4eec9d5ee5b5bcf/u_ex16031415.log")
    # with codecs.open("raw.txt","w","utf-8") as f:
    #   f.write(response)
    # url = "http://ic.snssdk.com/2/article/v25/stream/?count=20&min_behot_time=1457672142&bd_city=%E5%8C%97%E4%BA%AC%E5%B8%82&bd_latitude=40.08686&bd_longitude=116.336227&bd_loc_time=1457671953&loc_mode=7&loc_time=1457671306&latitude=40.092552660465&longitude=116.34280131795&city=%E5%8C%97%E4%BA%AC%E5%B8%82&iid=3827265717&device_id=7564326355&ac=wifi&channel=baidu&aid=13&app_name=news_article&version_code=466&device_platform=android&device_type=HM%202A&os_api=19&os_version=4.4.4&uuid=867711021068618&openudid=bd3fc32793ae8854&"
    # Url_Response_Json(url,"test2.json")
    # parsed_url = ParseUrl(url)
    # time_1min()
    # fi = "../ftp_data/201603151050.log"
    # Log_fuck(fi)
    #cur = datetime(2016,3,14)
    #pprint(cur)
    # cur="now"
    # Day_Log_Toutiao(cur,user_id="iid")
    argv = sys.argv
    if len(argv) == 3:
        Froms = argv[1]
        Tos = argv[2]
        From = datetime.strptime(Froms,"%Y%m%d")
        To = datetime.strptime(Tos,"%Y%m%d")
        # Day_Log_Toutiao(From,To)
    elif len(argv) == 2:
        now = datetime.strptime(argv[1],"%Y%m%d")
        Day_Log_Toutiao(now,user_id="iid")

    elif len(argv) == 1:
        now = datetime.now()
        Day_Log_Toutiao(now,user_id="iid")

    else:
        print("fromat: year_month_day year_month_day")
        print("or nothing")