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
import asyncio
from tqdm import tqdm
import aiohttp

sys.setrecursionlimit(1000000)#防止迭代超过上限报错
LogPath=os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs/logs.yaml")
MainLoggerConfig.setup_logging(default_path=LogPath)
logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)

class load_biquge(object):

    logger = logging.getLogger(__name__)

    def __init__(self,mother_url):

        self.mother_url=mother_url#文章链接
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

    def get_page_url(self):
        '''
        解析目标小说链接，返回章节链接
        :return: 返回章节链接
        '''
        mode_page=self.html_parse(self.mother_url)
        ddList = mode_page.find_all("dd")
        return [dd.find("a").get("href") for dd in ddList if dd.find("a")]

    async def get_one_page(self,page_url):
        '''
        异步获取一个章节链接，保存为txt文件
        :param page_url: 章节链接
        :return:
        '''
        # time.sleep(1)
        text = []
        self.logger.debug("load a page_url:%s"%page_url)
        print("下载开始")
        page_content= await self.async_html_parse(page_url)
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
                print("下载结束")
                self.logger.debug("Successfully downloaded a file:%s.txt" % title)
        else:
            print("err!")

    async def async_html_parse(self,url):
        '''
        异步获取指定url的response
        :param url:
        :return:
        '''
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko)"
                                 " Chrome/63.0.3239.132 Safari/537.36"}
        session=aiohttp.ClientSession()
        try:
            response=await session.get(url,headers=headers)
            if response.status_code==200:
                return BeautifulSoup(response.text, "html.parser")
        except RequestException as e:
            print(e.args)
        return None

    # async def main(self):
    #     '''
    #     windows不支持fork，无法用多进程协程
    #     '''
    #     async with aiomultiprocess.Pool(5) as pool:
    #         result= await pool.map(func=m.get_one_page, iterable=self.get_page_url())
    #         return result

if "__main__"==__name__:

    # m= load_biquge('https://www.biquge5200.cc/0_844')
    # croutine=m.main()
    # tasks=asyncio.ensure_future(croutine)
    # loop=asyncio.get_event_loop()
    # loop.run_until_complete(tasks)

    m = load_biquge('https://www.biquge5200.cc/0_844')
    tasks=[asyncio.ensure_future(m.get_one_page(url)) for url in m.get_page_url()]
    loop=asyncio.get_event_loop()
    loop.run_until_complete(asyncio.wait(tasks))










