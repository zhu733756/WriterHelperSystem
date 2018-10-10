# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：    load_biquke.py
   Description：
-------------------------------------------------
__author__ = 'ZH'
"""
from requests import RequestException
from bs4 import BeautifulSoup
import re,os,requests,logging,sys,time
from SpiderUtils import MainLoggerConfig
from multiprocessing import Pool
from tqdm import tqdm
import urllib3
urllib3.disable_warnings()
sys.setrecursionlimit(1000000)#防止迭代超过上限报错
LogPath=os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs/logs.yaml")
MainLoggerConfig.setup_logging(default_path=LogPath)
logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)

class load_biquge(object):

    logger = logging.getLogger(__name__)

    def __init__(self,mother_url):

        self.mother_url=mother_url#文章链接
        self.valid_urls=[]
        self.useful_proxy=""
        self.path = self.get_path()

    def get_path(self):
        '''
        获取存储目录
        :return:
        '''
        first_page=self.html_parse(self.mother_url)
        path="./data/{}/{}". \
            format(first_page.find("p").string.strip().split("：")[-1],
                   first_page.find("div",{"id":"info"}).find("h1").string)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def get_proxy(self):
        proxy_url="http://localhost:5555/random"
        try:
            response=requests.get(proxy_url)
            if response.status_code==200:
                return {
                    "http":"http://"+response.text,
                    "https":"https://"+response.text
                }
        except ConnectionError:
            return None

    @staticmethod
    def get_response(url,proxies):
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) "
                                      "AppleWebKit/537.36 (KHTML, like Gecko)"
                                      " Chrome/63.0.3239.132 Safari/537.36"}
        return requests.get(url, proxies=proxies,
                                        headers=headers)

    def valid_test(self,url):
        '''
        代理不可用时，切换代理
        :param url:
        :return:
        '''
        count=1
        while 1:
            try:
                if self.useful_proxy:
                    proxies=self.useful_proxy
                else:
                    proxies=self.get_proxy()
                if count >10:
                    proxies=None
                response = self.get_response(url,proxies)
                if response.status_code == 200:
                    self.useful_proxy=proxies
                    return response
            except Exception:
                pass
            if proxies:
                print(proxies["http"].split("/")[-1],\
                                  "runs wrong,change another!")
            count = count + 1

    def html_parse(self,url):
        '''
        解析网页返回beautifulsoap对象
        :param url: url
        :return: beautifulsoap对象
        '''
        # response=self.valid_test(url)
        try:
            response=self.get_response(url,proxies=None)
        except RequestException as e:
            print(e.args)
        else:
            return BeautifulSoup(response.content.decode("gbk"),"html.parser")
        return 

    def get_one_page(self,page_url):
        '''
        获取一个章节链接，保存为txt文件
        :param page_url: 章节链接
        :return:
        '''
        text=[]
        self.logger.debug("load a page_url:%s"%page_url)
        time.sleep(1)
        page_content=self.html_parse(page_url)
        if page_content:
            title = re.compile(r"\*").sub("", page_content.find("h1").string).strip()
            txt_content=page_content.find("div",id="content").stripped_strings
            for i in txt_content:
                if re.search(r"52bqg\.com",i):
                    continue
                text.append(i)
            else:
                with open(os.path.join(self.path,title+".txt"),
                          "w+",encoding="utf-8") as f:
                    f.write("\n".join(text))
                self.logger.debug("Successfully downloaded a file:%s.txt" % title)
        else:
            self.valid_urls.append(url)

    def get_page_url(self):
        '''
        解析目标小说链接，返回章节链接
        :return: 返回章节链接
        '''
        mode_page=self.html_parse(self.mother_url)
        ddList = mode_page.find_all("dd")
        return [dd.find("a").get("href") for dd in ddList if dd.find("a")]

if "__main__"==__name__:

    m = load_biquge("https://www.biquge5200.cc/0_844")

    try:
        with Pool(5) as pool:
            pool.map(func=m.get_one_page, iterable=m.get_page_url())
        if m.valid_urls:
            with Pool(5) as pool:
                pool.map(func=m.get_one_page, iterable=m.valid_urls)
    except Exception as e:
        m.logger.error("Pool Err:",e.args)









