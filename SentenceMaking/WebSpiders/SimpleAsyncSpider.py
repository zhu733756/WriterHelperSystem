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
import re,os,requests,logging,sys,time,asyncio,aiohttp
# from SpiderUtils import MainLoggerConfig
from tqdm import tqdm
from queue import LifoQueue

sys.setrecursionlimit(1000000)#防止迭代超过上限报错
# LogPath=os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs/logs.yaml")
# MainLoggerConfig.setup_logging(default_path=LogPath)
# logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)

class load_biquge(object):

    logger = logging.getLogger(__name__)

    def __init__(self,mother_url):

        self.mother_url=mother_url#文章链接
        self.q=LifoQueue()
        self.total=None
        self.path = self.get_path()

    def get_path(self):
        '''
        获取存储目录
        :return:
        '''
        first_page=self.html_parse(self.mother_url)
        path=r"./data/{}/{}". \
            format(first_page.find("p").string.strip().split("：")[-1],
                   first_page.find("div",{"id":"info"}).find("h1").string)
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def html_parse(self,url):
        '''
        解析网页返回beautifulsoap对象
        :param url: url
        :return: beautifulsoap对象
        '''
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko)"
                                 " Chrome/63.0.3239.132 Safari/537.36"}
        try:
            response=requests.get(url,headers=headers)
            if response.status_code==200:
                return BeautifulSoup(response.text, "html.parser")
        except RequestException as e:
            print(e.args)
        return None

    def put_page_url(self):
        '''
        解析目标小说链接，返回章节链接
        :return: 返回章节链接
        '''
        mode_page=self.html_parse(self.mother_url)
        ddList = mode_page.find_all("dd")
        for dd in ddList[:100]:
            self.q.put(dd.find("a").get("href"))
        self.total=len(self.q.queue)
        print("total",self.total)

    async def async_html_parse(self,url):
        '''
        异步获取指定url的response
        :param url:
        :return:
        '''
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko)"
                                 " Chrome/63.0.3239.132 Safari/537.36"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as response:
                    assert response.status ==200
                    result=await response.text()
                    page_content=BeautifulSoup(result,"html.parser")
                    text=[]
                    title = re.compile(r"\*").sub("", page_content.find("h1").string).strip()
                    txt_content = page_content.find("div", id="content").stripped_strings
                    for i in txt_content:
                        if re.search(r"52bqg\.com", i):
                            continue
                        text.append(i)
                    with open(os.path.join(os.path.realpath(self.path),title)+ '.txt', "w+", encoding="utf-8") as f:
                        f.write("\n".join(text))
                    self.logger.debug("Successfully downloaded a file:%s.txt" % title)

    def get_queue(self):
        while True:
            count = 0
            tasks = []
            while count <= 9:
                if not self.q.empty():
                    url= self.q.get()
                    tasks.append(asyncio.ensure_future(self.async_html_parse(url)))
                else:
                    break
                count +=1
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            if self.q.empty():
                break
            time.sleep(2)
            print("left",len(self.q.queue))
#
if __name__ =="__main__":

    t=time.time()
    m=load_biquge("https://www.biquge5200.cc/7_7222/")
    m.put_page_url()
    m.get_queue()
    print(time.time()-t)











