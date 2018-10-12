# -*- coding: utf-8 -*-
"""
@author: zh
"""
import os,sys
from MultiprocessAsyncSpider import load_biquge
from split_words import generate_key
import requests,re,time
from multiprocessing import Process,Manager,Queue


class Crawler(object):

    totalProgress={}

    def __init__(self,q):
        self.q=q
        self.seen=set()

    def download(self,req):
        ins=load_biquge(req)
        ins.put_page_urls()
        # self.totalProgress.setdefault(req,ins.total)
        self.totalProgress.setdefault(req,ins.getProgressPercent())
        p1 = Process(name="CrawlProcess-1", target=ins.get_queue, args=())
        p2 = Process(name="CrawlProcess-2", target=ins.get_queue, args=())
        p3 = Process(name="ProgressProcess", target=ins.ShellProgress, args=())
        for p in (p1, p2, p3):
            p.start()
        for p in (p1, p2, p3):
            p.join()

    def filter(self,items):
        for item in items:
            if item not in self.seen:
                yield item
                self.seen.add(item)

    def push(self,items):
        for req in items:
            self.q.put(req)

    def check(self,item):
        return item in self.seen

    def crawl(self):
        print("Wait for req...")
        while 1:
            if not self.q.qsize():
               req=self.q.get()
            else:
               req=self.q.get_nowait()
            self.download(req)

q1 = Queue()
crawler = Crawler(q1)

if "__main__"==__name__:

    import sys

    sys.path.append(os.path.dirname(os.path.realpath(__file__)))

    items=Manager().list(["https://www.biquge5200.cc/0_46/"])
    # p1=Process(target=crawler.crawl,args=())
    # p2=Process(target=crawler.push,args=(items,))
    # for p in (p1,p2):
    #     p.start()
    # for p in (p1,p2):
    #     p.join()
    import subprocess
    subprocess.Popen(["Crawler.crawler.crawl()"],shell=True)
    print("done!")






