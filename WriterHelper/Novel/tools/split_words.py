# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
import os,re,jieba,sys
import jieba.posseg as pseg
import json
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
sys.setrecursionlimit(1000000)#防止迭代超过上限报错

# logger=logging.getLogger("spider.sub")

BaseDir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class lazyproperty(object):

    def __init__(self,func):
        self.func=func

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            value=self.func(instance)
            setattr(instance,self.func.__name__,value)
            return value

class SentenceMaking(object):

    def __init__(self,mode=None,key=None):
        if mode is None:
            raise ValueError("Expected a mode!")
        if key not in ("verb", "idiom"):
            raise ValueError("Cannot find such key(%s)" % key)
        self.mode=mode
        self.key=key
        self.split_keywords={}

    @lazyproperty
    def idioms(self):
        return json.dumps(list(pd.read_json(
                    os.path.join(BaseDir,'ChineseXinhua\\idiom.json'),
                    encoding="utf-8").loc[:, "word"]))

    @lazyproperty
    def stopwords(self):
        return  "".join(map(str.strip,
                        open(os.path.join(BaseDir,"config\\stopwords.txt"),"r",
                             encoding="utf-8").readlines()))

    def get_total(self):
        return len(list(self.get_file_path()))

    def get_auther_and_title(self):
        title = os.path.split(self.mode)[-1]
        author = os.path.split(os.path.dirname(self.mode))[-1]
        return author, title

    def get_file_path(self):
        fiter_files=[filename \
                        for filename in os.listdir(self.mode) \
                        if re.search("(^第.*章.*)", filename)]
        for filename in fiter_files:
            yield os.path.join(self.mode, filename)

    @staticmethod
    def get_strings(path):
        return filter(lambda x: x,
                         map(str.strip, open(path,\
                        "r", encoding="utf-8").readlines()))

    def make_idioms(self,path):
        for sentence in self.get_strings(path):
            if sentence[0] in ('“', '”', '"', '"') or \
                            sentence[-1] in ('“', '”', '"', '"'):
                continue
            for tag in jieba.cut(sentence, cut_all=False):
                if len(tag) < 4:
                    continue
                if re.search("\d+",tag):
                    continue
                tag = tag.strip()
                if tag in json.loads(self.idioms):
                    self.split_keywords.setdefault("chapter", \
                                    os.path.split(path)[-1].split(".")[0])
                    self.split_keywords.setdefault(tag, []).append(sentence)
        if self.split_keywords:
            self.save_json()

    def make_verbs(self,path):
        for sentence in self.get_strings(path):
            if sentence[0] in ('“', '”', '"', '"') or \
                            sentence[-1] in ('“', '”', '"', '"'):
                continue
            for tag, flag in pseg.cut(sentence):
                tag = tag.strip()
                if not tag:
                    continue
                if tag.isdigit():
                    continue
                if flag == "v":
                    if tag[0] in "不无了就是":
                        continue
                    if len(tag) >= 2 and tag[1] in "不上下":
                        continue
                    if tag in self.stopwords:
                        continue
                    self.split_keywords.setdefault("chapter", \
                                    os.path.split(path)[-1].split(".")[0])
                    self.split_keywords.setdefault(tag, []).append(sentence)
        if self.split_keywords:
            self.save_json()

    def save_json(self):
        path="./Sentencekey/%s"%("-".join(self.get_auther_and_title()))
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path,self.key)+".json",\
                  "a+",encoding="utf-8") as f:
            f.write(json.dumps(self.split_keywords,
                               ensure_ascii=False,)+"\n")

def generate_key(mode,key):
    instance = SentenceMaking(mode,key)
    author,title=instance.get_auther_and_title()
    total = instance.get_total()
    func_name="make_"+key+"s"
    if hasattr(instance,func_name):
        func=getattr(instance,func_name)
    with Pool(5) as pool:
        _ = [x for x in tqdm(
            pool.imap(func=func,iterable=instance.get_file_path())
                ,total=total,
                desc="Extract Key(%s|%s|%s)"% (author,title,key))]

if __name__ == "__main__":

    generate_key("./NovelsRawData/失落叶/天行","verb",)
    generate_key("./NovelsRawData/天蚕土豆/斗破苍穹","idiom")




