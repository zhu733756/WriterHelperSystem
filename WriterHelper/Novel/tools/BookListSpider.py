# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
import re,requests
from requests import RequestException

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
