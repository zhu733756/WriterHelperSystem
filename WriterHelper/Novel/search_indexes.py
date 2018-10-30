# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     
   Description：
-------------------------------------------------
__author__ = 'zhu733756'
"""
from haystack import indexes
from .models import Arcticle


class ArcticleIndex(indexes.SearchIndex,indexes.Indexable):

    text=indexes.CharField(document=True,use_template=True)

    def get_model(self):
        return  Arcticle

    def index_queryset(self, using=None):
        return self.get_model().objects.all()

