# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
import pandas as pd
import os,json,re,sys
sys.setrecursionlimit(9999999)

class SearchRes(object):

    Base_Dir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    idioms_path=os.path.join(Base_Dir,"SentenceMaking\ChineseXinhua\idiom.json")
    novels_path=os.path.join(Base_Dir,"SentenceMaking\Sentencekey")

    def __init__(self,data=None):
        self._data=data

    def search_idioms(self):
        if len(self._data["words"]) < 4:
            return ""
        idioms=pd.read_json(self.idioms_path,encoding="utf-8")
        if any(idioms.loc[:,"word"].str.contains(self._data["words"])):
            result=idioms[idioms.word==self._data["words"]]
            index=list(result.index)[0]
            res_en=result.to_dict("index")[index]
            mapping={"derivation":"出处","example":"造句","explanation":"解释","pinyin":"拼音"}
            return {v:res_en[k] for k,v in mapping.items()}
        else:
            return "no such idioms!"

    def search_novels(self):

        if len(self._data["words"]) <= 2:
            searchJsonKey="verb"
        else:
            searchJsonKey="idiom"

        searchLic = []
        info = {}
        for path in self.find_searchKey(searchJsonKey):
            with open(path,"r",encoding="utf-8") as f:
                novel_info = os.path.split(os.path.dirname(path))[-1]
                lines=(line for line in f.read().split("\n") if line)
                try:
                    for line in lines:
                        line = json.loads(line.strip())
                        chapter = line["chapter"].replace(" ", "_")
                        if self._data["words"] in line:
                            info.setdefault(novel_info, {}). \
                                setdefault(chapter, []) \
                                    .extend(line[self._data["words"]])
                    else:
                        if info:
                            searchLic.append(info)
                            info={}
                except json.JSONDecodeError as e:
                        print("ERR(%s-%s)" % (path, e.args))
        if searchLic:
            if len(searchLic) >1000:
                return searchLic[:1000]
            return searchLic
        else:
            return "no such %ss in novels!"%searchJsonKey

    @staticmethod
    def find_searchKey(searchKey):

        for dirname in os.listdir(SearchRes.novels_path):
            file_path=SearchRes.novels_path+"\\"+dirname
            if os.path.isdir(file_path):
                yield file_path+"\\"+searchKey+".json"

    def search(self):
        func_name = "search_{}".format(self._data["key"])
        if hasattr(self, func_name):
            func = getattr(self, func_name)
            return func()
        else:
            return "没有此方法！"

# print(SearchRes({"key":"novels","words":"登峰造极"}).search())
