# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：    load_biquke.py
   Description：
-------------------------------------------------
__author__ = 'ZH'
"""
import os,sys
from requests import RequestException
from bs4 import BeautifulSoup
import re,requests,logging,time,asyncio,aiohttp
from tqdm import tqdm
from multiprocessing import Process,Queue
# from split_words import lazyproperty
# from SpiderUtils import MainLoggerConfig

sys.setrecursionlimit(1000000)#防止迭代超过上限报错
# MainLoggerConfig.setup_logging()
# logging.getLogger("urllib3.connectionpool").setLevel(logging.INFO)

class load_biquge(object):

    # logger = logging.getLogger(__name__)

    def __init__(self,mother_url=None):

        self.mother_url = mother_url#文章链接
        self.q = Queue()
        self.total = None
        self.invalid_q = Queue()
        self.path=self.get_path()

    def get_path(self):
        '''
        获取存储目录
        :return:
        '''
        BaseDir=os.path.dirname(os.path.dirname
                                (os.path.dirname(os.path.dirname(__file__))))
        first_page=self.html_parse(self.mother_url)
        path=os.path.join(BaseDir,r"SentenceMaking\NovelsRawData\{}\{}". \
            format(first_page.find("p").string.strip().split("：")[-1],
                   first_page.find("div",{"id":"info"}).find("h1").string))
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            self.check_downloaded(path)
        return path

    def check_downloaded(self,path):
        '''
        获取当前目录已经爬取的数目
        :param path:
        :return:
        '''
        self.downloadedNum=len([file for file in os.listdir(path)])

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

    def put_page_urls(self):
        '''
        解析目标小说链接，返回全部章节链接
        :return:
        '''
        mode_page=self.html_parse(self.mother_url)
        ddList = mode_page.find_all("dd")
        if hasattr(self,"downloadedNum"):
            ddList=ddList[self.downloadedNum:]
        for dd in ddList:
            self.q.put(dd.find("a").get("href"))
        self.total=self.q.qsize()
        print("Total queue(url:%s):"%self.mother_url,self.total)

    async def async_html_parse(self,url):
        '''
        异步获取指定url的response,并保存为txt文件
        :param url:
        :return:
        '''
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.1) "
                                 "AppleWebKit/537.36 (KHTML, like Gecko) "
                                 "Chrome/63.0.3239.132 Safari/537.36"}
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers=headers) as response:
                if response.status ==200:
                    try:
                        result=await response.text()
                    except:
                        result=await response.text(encoding='GB18030')
                    page_content = BeautifulSoup(result, "html.parser")
                    title = re.compile(r"[*.?？<>:：【】]+")\
                        .sub("", page_content.find("h1").string).strip()
                    title=re.compile("\s+").sub(" ",title)
                    text = page_content.find("div", id="content").stripped_strings
                    with open(os.path.join(self.path, title) + '.txt',
                              "w+", encoding="utf-8") as f:
                        f.write("\n".join(text))
                else:
                    self.invalid_q.put(url)

    def getProgressLeft(self):
        return self.q.qsize() + self.invalid_q.qsize()

    def getProgressPercent(self):
        return int((1-self.getProgressLeft()/self.total)*100)

    def ShellProgress(self,TimeOutNum=5):
        pbar = tqdm(total=self.total)
        same_update=0
        found=0
        while 1:
            tmp = self.getProgressLeft()
            if not tmp or found>=TimeOutNum:
                pbar.update(self.total-pbar.n)
                break
            if self.total-tmp-pbar.n <0:
                update =0
            else:
                update=self.total-tmp-pbar.n
            if tmp < 10 and update == same_update:
                found += 1
            else:
                found=0
            same_update=update
            pbar.update(update)
            time.sleep(2)
        pbar.close()

    def get_queue(self,):
        '''
        获取队列，启动协程异步程序，失效队列重爬
        :return:
        '''
        found = 0
        while 1:
            count = 0
            tasks = []
            if self.q.empty():
                break
            while count <= 9:
                if self.q.empty():break
                url= self.q.get()
                tasks.append(asyncio.ensure_future(self.async_html_parse(url)))
                count +=1
            loop = asyncio.get_event_loop()
            loop.run_until_complete(asyncio.wait(tasks))
            time.sleep(2)
            if self.has_valid_urls() and self.q.qsize() < 0.1 *self.total:
                self.put_valid_urls()

    def has_valid_urls(self):
        '''
        判断是否有失效url
        :return:
        '''
        return self.invalid_q.qsize() !=0

    def put_valid_urls(self):
        '''
        将失效url加入主队列
        :return:
        '''
        while 1:
            if self.invalid_q.empty():
                break
            url= self.invalid_q.get()
            self.q.put(url)

if __name__ =="__main__":

    m=load_biquge('https://www.biquge5200.cc/0_46/')
    m.put_page_urls()
    p1 = Process(name="CrawlProcess-1", target=m.get_queue, args=())
    p2 = Process(name="CrawlProcess-2", target=m.get_queue, args=())
    p3 = Process(name="ProgressProcess", target=m.ShellProgress, args=())
    for p in (p1,p2, p3):
        p.start()
    for p in (p1,p2, p3):
        p.join()














