# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
from  datetime import datetime
from haystack import indexes
from .models import Arcticle


class ArcticleIndex(indexes.SearchIndex,indexes.Indexable):

    text=indexes.CharField(document=True,use_template=True)
    author=indexes.CharField(model_attr="authors")
    pub_time=indexes.DateTimeField(model_attr="pub_time")

    def get_model(self):
        return  Arcticle

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(pub_time__lte==datetime.now())

