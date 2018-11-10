#!/usr/bin/python
# -*- coding: UTF-8 -*-

import ConfigParser
import shelve
import aiml
import jieba

from crawler import Crawler
from deeplearning import deeplearning
from filter import *


class ChatBot:
    """
        Intelligent dialogue model based on AIML and WebQA
        1. AIML 
        2. WebQA
        3. Deeplearning

        usage:
        bot = ChatBot()
        print bot.response('Hello')
    """

    def __init__(self, config_file='config.cfg'):
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self.filter_file = config.get('resource', 'filter_file')
        self.load_file = config.get('resource', 'load_file')
        self.save_file = config.get('resource', 'save_file')
        self.shelve_file = config.get('resource', 'shelve_file')

        # Initialization 
        jieba.initialize()

        # Initialize the filter
        self.gfw = DFAFilter()
        self.gfw.parse(self.filter_file)

        # Initialize the knowledge base
        self.mybot = aiml.Kernel()
        self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')

        # Initialize the learning library
        self.template = '<aiml version="1.0" encoding="UTF-8">\n{rule}\n</aiml>'
        self.category_template = '<category><pattern>{pattern}</pattern><template>{answer}</template></category>'

    def response(self, message):
        # Limit word count
        if len(message) > 60:
            return self.mybot.respond('MAX')
        elif len(message) == 0:
            return self.mybot.respond('MIN')

        # Filter sensitive words
        message = self.gfw.filter(message, "*")
        if message.find("*") != -1:
            return self.mybot.respond('filter')

        # End chat
        if message == 'exit' or message == 'quit':
            return self.mybot.respond('Thank you for using RazChatbot. Goodbye')
        # Start chatting
        else:
            ########
            # AIML #
            ########
            result = self.mybot.respond(' '.join(jieba.cut(message)))

            # Matching mode
            if result[0] != '#':
                return result
            # Search mode
            elif result.find('#NONE#') != -1:
                #########
                # WebQA #
                #########
                #ans = Crawler.search(message)
                ans=''
                if ans != '':
                    return ans.encode('utf-8')
                else:
                    ###############
                    # Deeplearing #
                    ###############
                    ans = deeplearning.tuling(message)
                    return ans.encode('utf-8')
            # Learning mode
            elif result.find('#LEARN#') != -1:
                question = result[8:]
                answer = message
                self.save(question, answer)
                return self.mybot.respond('Already studied')
            # MAY BE BUG
            else:
                return self.mybot.respond('Sorry, I don\'t know.')

    def save(self, question, answer):
        db = shelve.open(self.shelve_file, 'c', writeback=True)
        db[question] = answer
        db.sync()
        rules = []
        for r in db:
            rules.append(self.category_template.format(pattern=r, answer=db[r]))
        with open(self.save_file, 'w') as fp:
            fp.write(self.template.format(rule='\n'.join(rules)))

    def forget(self):
        import os
        os.remove(self.save_file) if os.path.exists(self.save_file) else None
        os.remove(self.shelve_file) if os.path.exists(self.shelve_file) else None
        self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')


if __name__ == '__main__':
    bot = ChatBot()
    while True:
        message = raw_input('ME > ')
        print 'AI > ' + bot.response(message)
