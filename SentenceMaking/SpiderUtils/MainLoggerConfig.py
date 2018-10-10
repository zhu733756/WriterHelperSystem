# -*- coding: utf-8 -*-
"""
@author: zh
"""
import logging,os,yaml
from logging.config import dictConfig

LogPath=os.path.join(os.path.dirname(os.path.realpath(__file__)),"logs\\logs.yaml")

def setup_logging(default_path=LogPath,default_level = logging.INFO):

    if os.path.exists(default_path):
        with open(default_path,"r") as f:
            dictConfig(yaml.load(f))
    else:
        logging.basicConfig(level = default_level)









