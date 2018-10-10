# -*- coding: utf-8 -*-
"""
@author: zh
"""
import os,sys
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.join(BASE_DIR,"SentenceMaking"))

from WebSpiders.MultiprocessAsyncSpider import *
from SplitWords.split_words import *
import requests,re
from redis import StrictRedis,ConnectionPool
from requests import RequestException
from multiprocessing import Process

class FIFOQueue(object):

    def __init__(self,redis_key=None):

        self.redis=StrictRedis(
            connection_pool=ConnectionPool(host="localhost",port=6379))
        self.seen=set()
        self.redis_key=redis_key

    def get_seens(self,items):
        for item in items:
            if item not in self.seen:
                yield item
                self.seen.add(item)

    def push(self,items):
        for url in self.get_seens(items):
            if url:
                self.redis.lpush(self.redis_key, url)


    def pop(self):
        return self.redis.lpop(self.redis_key)

    def size(self):
        return self.redis.llen(self.redis_key)

FIFO_q=FIFOQueue("Novels:start_urls")

class Crawler(object):

    on_progress=[]

    def __init__(self):
        self._q=FIFO_q

    def download(self,req):
        m = load_biquge(req)
        m.put_page_urls()
        p1 = Process(name="CrawlProcess-1", target=m.get_queue, args=())
        p2 = Process(name="CrawlProcess-2", target=m.get_queue, args=())
        p3 = Process(name="ProgressProcess", target=m.ShellProgress, args=())
        for p in (p1, p2, p3):
            p.start()
        for p in (p1, p2,p3):
            p.join()
        if not p3.is_alive():
            self.on_progress.remove(req)

    def next_requests(self):
        found=0
        while found < self._q.size():
            req= self._q.pop()
            if not req:
                break
            self.on_progress.append(req)
            yield req
            found += 1

    def filter(self,items):
        return self._q.get_seens(items)

    def push(self,items):
        self._q.push(items)

    def crawl(self,reason=None):
        while 1:
            if self._q.size():
                for req in self.next_requests():
                    self.download(req)
            if reason=="break":
                break

crawler=Crawler()

class BookInfoSpider(object):

    def split_search_key(self,*args,**kwargs):
        arg_res = []
        kw_res = []

        if args:
            for searchkey in args:
                tmp=self.html_parser(searchkey)
                if tmp:
                    arg_res.extend(tmp)
            if arg_res:
                arg_res=self.remove_duplicate(arg_res)

        if kwargs:
            for author,bookname in kwargs.items():
                author_search=self.html_parser(author,"author")
                if author_search :
                    if bookname == author_search["bookname"]:
                        kw_res.append(author_search)
                    break
                else:
                    bookname_search=self.html_parser(bookname,"bookname")
                    kw_res.extend(bookname_search)

        all_res=[]
        if arg_res and kw_res:
            all_res.extend(arg_res)
            all_res.extend(kw_res)
            all_res=self.remove_duplicate(all_res)
        else:
            all_res=arg_res if arg_res else kw_res

        sorted_res = {}
        for info in all_res:
            author=info.pop("author")
            sorted_res.setdefault(author, []).append(info)
        return sorted_res

    @staticmethod
    def remove_duplicate(dup_list):
        seen=set()
        for lis in dup_list:
            author=lis["author"]
            bookname=lis["bookname"]
            if (author,bookname) not in seen:
                yield lis
                seen.add((author,bookname))

    def html_parser(self,search_key,mode="all"):
        search_url='https://www.biquge5200.cc/modules/article/search.php?searchkey=%s'%search_key
        pattern=re.compile(
            r'.*?<tr>.*?'
            r'<td class="odd">.*?<a href="(.*?)">(.*?)</a>.*?</td>.*?'
            r'<td class="odd">(.*?)</td>.*?'
            r'<td class="odd" align=".*?">(.*?)</td>.*?'
            r'</tr>.*?',re.S)
        try:
            page_content=requests.get(search_url).text
            result=re.findall(pattern,page_content)
            resList=[]
            for res in result:
                book_info={
                    "href":res[0],
                    "bookname":res[1],
                    "author":res[2],
                    "update_time":res[3]
                    }
                if mode=="bookname":
                    if res[1]==search_key:
                        resList.append(book_info)
                if mode == "author":
                    if res[2]==search_key:
                        return book_info
                if mode == "all":
                    if res[1] == search_key or res[2] == search_key:
                        resList.insert(0,book_info)
                    else:
                        resList.append(book_info)
            return resList
        except RequestException as e:
            print("RequestException:%s"%e.args)

if __name__=="__main__":

    crawler.crawl()
