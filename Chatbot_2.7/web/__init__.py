import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from chatbot import ChatBot
bot = ChatBot()

from flask import Flask
app = Flask(__name__, static_url_path='')


import logging
from logging.handlers import TimedRotatingFileHandler

def init_log(log_file='log/info.log'):
    """
    Split the log by day
    interval: Rolling cycle
    backupCount: Number of backups
    """
    handler = TimedRotatingFileHandler(log_file, when="D", interval=1, backupCount=7)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    return logger


logger = init_log()