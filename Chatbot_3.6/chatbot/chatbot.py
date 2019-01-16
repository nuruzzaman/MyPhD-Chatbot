import configparser
import shelve
import aiml
import colorama
import wordsegment as ws
import os 
import sys
import string

import mysql.connector
import tensorflow as tf
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize 

from itertools import groupby
from stanfordcorenlp import StanfordCoreNLP

import chatbot.crawler as crawler
import chatbot.deeplearning as deep
import chatbot.kdddatabased as kb
from settings import PROJECT_ROOT
from chatbot.botpredictor import BotPredictor




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
        
        corp_dir = os.path.join(PROJECT_ROOT, 'Data', 'Corpus')
        knbs_dir = os.path.join(PROJECT_ROOT, 'Data', 'KnowledgeBase')
        res_dir = os.path.join(PROJECT_ROOT, 'Data', 'Result')
    
        # Initialize the KERNEL 
        self.mybot = aiml.Kernel()
        sess = tf.Session()
        self.predictor = BotPredictor(sess, corpus_dir=corp_dir, knbase_dir=knbs_dir, result_dir=res_dir, result_file='basic')
        self.session_id = self.predictor.session_data.add_session()
                                    
        # Create AI Engine 
        if os.path.isfile("model\AIChatEngine.brn"):
            self.mybot.bootstrap(brainFile = "model\AIChatEngine.brn")            
        else:
            self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')
            self.mybot.saveBrain("model\AIChatEngine.brn")
            
        # Use an existing server: StanfordCoreNLP
        self.nlp = StanfordCoreNLP('http://localhost', port=9000)

################################################################
            
    def response(self, user_message):
        # Limit word count
        if len(user_message) > 100:
            return self.mybot.respond('MAX')
        elif len(user_message) == 0:
            return self.mybot.respond('MIN')
        
        # Start chatting
        else:
            #print ('# User original message # > ' + user_message)
            # Word Segmentation: split words e.g. hellohowareyou --> hello how are you
            #segmented_text = ' '.join(ws.segment(user_message))
            #print('# After Segmentation # >'+segmented_text)
            
            
            # Init Lemmatization 
            wordnet_lemmatizer = WordNetLemmatizer()            
            
            # User Input Sentence Tokenization 
            word_tokens = word_tokenize(user_message) 
            
            # Removing stopwords
            stop_words = set(stopwords.words('english')) 
            filtered_sentence = [w for w in word_tokens if not w in stop_words] 
            filtered_stop_words = [] 
            for w in word_tokens: 
                if w not in stop_words: 
                    filtered_stop_words.append(w) 
            
            print(colorama.Fore.RED+'\n------------------ User Input Words --> Lemma -------------------------- '+colorama.Fore.RESET)
            final_sentence = [] 
            for word in filtered_stop_words:
                final_sentence.append(wordnet_lemmatizer.lemmatize(word, pos="v")) 
                print ("{0:10}{1:5}{2:20}".format(word, '--> ', wordnet_lemmatizer.lemmatize(word, pos="v")))
            
            
            # POS Tagger 
            postagger = self.nlp.pos_tag(' '.join(final_sentence))
            print(colorama.Fore.YELLOW+'\n------------------ Identify POS Tagger -------------------------- '+colorama.Fore.RESET)
            print('pos tagger: ', postagger)
            
            # Add all NOUNs into list 
            nounEntityList = [] 
            for pos in postagger:
                if pos[1] in ('NN','NNS','NNP','NNPS'):
                    nounEntityList.append(pos[0])
            print(colorama.Fore.GREEN+'\n------------------ Added NOUN into Entity List ------------------------- '+colorama.Fore.RESET) 
            print(nounEntityList, '\n')
            
            #depparse = self.nlp.dependency_parse(' '.join(final_sentence))
            #print(depparse)
            
            botresponse = self.mybot.respond(user_message)
            print ('# Bot > ' + botresponse)
            
            responseAnswer = '' 
            # Template-based mode
            if botresponse[0] != '#':
                responseAnswer = botresponse
            
            elif botresponse.find('#NONE#') != -1: 
                # KB Searching mode  #
                ######################
                ans = ''
                ans = kb.kdd_search(nounEntityList)
                if ans != '':
                    responseAnswer = ans.encode('utf-8')
                else:
                    # WEB Searching mode #
                    ######################
                    #ans = crawler.web_search(user_message)
                    if ans != '':
                        responseAnswer = ans.encode('utf-8')
                    else:
                        # DEEP Learing- RNN #
                        #####################
                        ans = deep.neural_network(self, user_message)
                        responseAnswer = ans.encode('utf-8')
            
            # Self-Learning Mode
            elif botresponse.find('#LEARN#') != -1:
                print ('Learning Mode--> ' +botresponse)
                question = botresponse[8:]
                answer = user_message
                self.save(question, answer)
                responseAnswer = self.mybot.respond('Already studied')
                
            # check for BUG
            else:
                responseAnswer = self.mybot.respond('I don\'t know.')
            
            return responseAnswer 

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
