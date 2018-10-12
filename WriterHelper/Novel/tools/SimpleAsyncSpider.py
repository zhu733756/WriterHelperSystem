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
from queue import Queue
from split_words import lazyproperty
from threading import Thread,Timer
from collections import deque

sys.setrecursionlimit(1000000)#防止迭代超过上限报错
# LogPath=os.path.join(os.path.dirname(os.path.dirname(__file__)),"logs/logs.yaml")
# MainLoggerConfig.setup_logging(default_path=LogPath)
# logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)

class load_biquge(object):

    # logger = logging.getLogger(__name__)

    def __init__(self,mother_url=None):

        self.mother_url=mother_url#文章链接
        self._q=Queue()
        self.invalid_q=Queue()
        self.total=None

    @lazyproperty
    def path(self):
        '''
        获取存储目录
        :return:
        '''
        BaseDir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        first_page=self.html_parse(self.mother_url)
        path=os.path.join(BaseDir,"\\NovelsRawData\\{}\\{}". \
            format(first_page.find("p").string.strip().split("：")[-1],
                   first_page.find("div",{"id":"info"}).find("h1").string))
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
            self._q.put(dd.find("a").get("href"))
        self.total=len(self._q.queue)
        print("total",self.total)

    async def async_html_parse(self,url):
        '''
        异步获取指定url的response
        :param url:
        :return:
        '''
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/63.0.3239.132 Safari/537.36"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    try:
                        result = await response.text()
                    except:
                        result = await response.text(encoding='GB18030')
                    page_content = BeautifulSoup(result, "html.parser")
                    title = re.compile(r"\*|\.|\?|？").sub("", page_content.find("h1").string).strip()
                    text = page_content.find("div", id="content").stripped_strings
                    with open(os.path.join(self.path, title) + '.txt',
                              "w+", encoding="utf-8") as f:
                        f.write("\n".join("".join(text)))
                else:
                    self.invalid_q.put(url)

    def getProgressStatus(self):
        left = self._q.qsize() + self.invalid_q.qsize()
        return left

    def ShellProgress(self):
        # global ins
        # ins.setdefault(self,deque(maxlen=5))
        pbar = tqdm(total=self.total)
        while True:
            tmp = self.getProgressStatus()
            if not tmp:
                pbar.update(self.total - pbar.n)
                break
            if self.total - tmp - pbar.n < 0:
                update = 0
            else:
                update = self.total - tmp - pbar.n
            # ins.append(int((self.total - tmp) / self.total * 100))
            pbar.update(update)
            time.sleep(1)
        pbar.close()

    def get_queue(self):
        '''
        获取队列，启动协程异步程序，失效队列重爬
        :return:
        '''
        while 1:
            count = 0
            tasks = []
            if self._q.empty():
                break
            while count <= 5:
                if self._q.empty(): break
                url = self._q.get()
                tasks.append(asyncio.ensure_future(self.async_html_parse(url)))
                count += 1
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            # ins.setdefault(self,deque(maxlen=10)).append(self.getProgressStatus())
            time.sleep(2)
            if self.has_valid_urls() and self._q.qsize() < 0.1 * self.total:
                self.put_valid_urls()

    def has_valid_urls(self):
        '''
        判断是否有失效url
        :return:
        '''
        return self.invalid_q.qsize() != 0

    def put_valid_urls(self):
        '''
        将失效url加入主队列
        :return:
        '''
        while 1:
            if self.invalid_q.empty():
                break
            url = self.invalid_q.get()
            self._q.put(url)

if __name__ =="__main__":

    ins = {}
    t=time.time()
    m=load_biquge("https://www.biquge5200.cc/7_7222/")
    m.put_page_url()
    m.get_queue()
    for p in (p1, p3):
        p.start()
    for p in (p1, p3):
        p.join()











