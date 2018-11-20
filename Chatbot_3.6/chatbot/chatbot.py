import configparser
import shelve
import aiml
import colorama
import wordsegment as ws
import os 
import mysql.connector

import chatbot.crawler as crawler
import chatbot.deeplearning as deep
import chatbot.knowledgebased as kb

from nltk import *
from itertools import groupby
from stanfordcorenlp import StanfordCoreNLP

class ChatBot:
    """
        Intelligent dialogue model based on-
        1. Template-based- AIML 
        2. Knowledge Based- MySQL  
        3. Web Search 
        4. Deep Learning: RNN 
    """
    
    # initialize
    colorama.init()
    ws.load()
    #nltk.download()
    
    def __init__(self, config_file='config.cfg'):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.load_file = config.get('resource', 'load_file')
        self.save_file = config.get('resource', 'save_file')
        self.shelve_file = config.get('resource', 'shelve_file')
        self.filter_file = config.get('resource', 'filter_file')        
        
        # Initialize the KERNEL 
        self.mybot = aiml.Kernel()
        
        # Create AI Engine 
        if os.path.isfile("model\AIChatEngine.brn"):
            self.mybot.bootstrap(brainFile = "model\AIChatEngine.brn")            
        else:
            self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')
            self.mybot.saveBrain("model\AIChatEngine.brn")            

    def response(self, user_message):
        # Limit word count
        if len(user_message) > 100:
            return self.mybot.respond('MAX')
        elif len(user_message) == 0:
            return self.mybot.respond('MIN')    
        
        # End chat
        if user_message == 'exit' or user_message == 'quit':
            return self.mybot.respond('Thank you for using Chatbot. Good Bye')         
        
        # Start chatting
        else:
            #print ('# User original message # > ' + user_message)
            # Word Segmentation: split words e.g. hellohowareyou --> hello how are you
            #segmented_text = ' '.join(ws.segment(user_message))
            #print('# After Segmentation # >'+segmented_text)
            
            # Use an existing server: StanfordCoreNLP
            nlp = StanfordCoreNLP('http://localhost', port=9000)
            postagger = nlp.pos_tag(user_message)
            print(colorama.Fore.YELLOW+'\n------------------ Pos Tagger -------------------------- '+colorama.Fore.RESET)
            print(postagger)
            
            entityList = [] 
            for pos in postagger:
                if pos[1] in ('NN','NNS','NNP','NNPS'):
                    entityList.append(pos[0])            
            print(colorama.Fore.YELLOW+'\n------------------ Entity List ------------------------- '+colorama.Fore.RESET) 
            print(entityList, '\n')
                                    
            #depparse = nlp.dependency_parse(user_message)
            #print(depparse)
            
            botresponse = self.mybot.respond(user_message)
            print ('# Bot response # > ' + botresponse)
            
            # Template-based mode
            if botresponse[0] != '#':
                return botresponse
            
            elif botresponse.find('#NONE#') != -1: 
                # KB Searching mode  #
                ######################
                ans = ''
                ans = kb.kdd_search(entityList)
                if ans != '':
                    return ans.encode('utf-8')
                else:
                    # WEB Searching mode #
                    ######################
                    #ans = crawler.web_search(user_message)
                    if ans != '':
                        return ans.encode('utf-8')
                    else:
                        # DEEP Learing- RNN #
                        #####################
                        ans = deep.rnn_generator(user_message)
                        return ans.encode('utf-8')
            
            # Self-Learning Mode
            elif botresponse.find('#LEARN#') != -1:
                print ('Learning Mode--> ' +botresponse)
                question = botresponse[8:]
                answer = user_message
                self.save(question, answer)
                return self.mybot.respond('Already studied')
                
            # check for BUG
            else:
                return self.mybot.respond('I don\'t know.')

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
        os.remove(self.save_file) if os.path.exists(self.save_file) else None
        os.remove(self.shelve_file) if os.path.exists(self.shelve_file) else None
        self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')


if __name__ == '__main__':
    bot = ChatBot()	
    while True:		
        user_message = raw_input('User > ')
        print ('Bot > ' + bot.response(user_message))
