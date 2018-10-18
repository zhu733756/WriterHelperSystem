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

BaseDir=os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

class lazyproperty(object):
    '''
    lazyproperty装饰器让一个类方法的结果加入缓存
    '''
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
    '''
    用于分词的类
    '''
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
        '''
        把新华词典结果集加入缓存
        :return:
        '''
        return json.dumps(list(pd.read_json(
                    os.path.join(BaseDir,'SentenceMaking\\ChineseXinhua\\idiom.json'),
                    encoding="utf-8").loc[:, "word"]))

    @lazyproperty
    def stopwords(self):
        '''
        把停止词加入缓存
        :return:
        '''
        return  "".join(map(str.strip,
                        open(os.path.join(BaseDir,"SentenceMaking\\config\\stopwords.txt"),"r",
                             encoding="utf-8").readlines()))

    def get_total(self):
        '''
        获取处理章节总数
        :return:
        '''
        return len(list(self.get_file_path()))

    def get_auther_and_title(self):
        '''
        返回作者和书籍信息
        :return:
        '''
        title = os.path.split(self.mode)[-1]
        author = os.path.split(os.path.dirname(self.mode))[-1]
        return author, title

    def get_file_path(self):
        '''
        返回过滤后的章节
        :return: iter
        '''
        fiter_files=[filename \
                        for filename in os.listdir(self.mode) \
                        if re.search("(^第.*章.*)", filename)]
        for filename in fiter_files:
            yield os.path.join(self.mode, filename)

    @staticmethod
    def get_strings(path):
        '''
        读取某一章的所有句子行，过滤空格行
        :param path:
        :return:
        '''
        return filter(lambda x: x.strip(),
                         map(str.strip, open(path,\
                        "r", encoding="utf-8").readlines()))

    def make_idioms(self,path):
        '''
        制作成语索引
        :param path:
        :return:
        '''
        for sentence in self.get_strings(path):
            if sentence[0] in ('“', '”', '"', '"',) or \
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
        '''
        制作动词索引
        :param path: 章节路径
        :return:
        '''
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
        '''
        保存为json数据
        :return:
        '''
        path=BaseDir+"\\SentenceMaking\\Sentencekey\\%s"\
                     %("-".join(self.get_auther_and_title()))
        if not os.path.exists(path):
            os.makedirs(path)
        with open(os.path.join(path,self.key)+".json",\
                  "a+",encoding="utf-8") as f:
            f.write(json.dumps(self.split_keywords,
                               ensure_ascii=False,)+"\n")

def generate_key(mode,key):
    '''
    根据key生成句子索引
    :param mode: 书籍父路径
    :param key: idiom or verb
    :return:
    '''
    instance = SentenceMaking(mode, key)
    author,title=instance.get_auther_and_title()
    filepath=BaseDir+"/SentenceMaking/Sentencekey/{}-{}".format(author,title)
    if os.path.exists(filepath) and  key+".json" in os.listdir(filepath):
        print( "{}-{}的{}分词已经完成，自动跳过....".format(author,title,key))
        return False
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

   split_path = os.path.join(BaseDir,"SentenceMaking\\NovelsRawData")
   for author in os.listdir(split_path):
       print("正在处理作家【{}】的小说....".format(author))
       for n,book in enumerate(os.listdir(os.path.join(split_path,author))):
           print("第{}本:{}".format(str(n+1),book))
           book_path=os.path.join(split_path,"{}\\{}".format(author,book))
           generate_key(book_path, "verb")
           generate_key(book_path,"idiom")







