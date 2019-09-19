import configparser
import shelve
import aiml
import colorama
import wordsegment as ws
import os 
import sys
import string
import json
import random

import language_check

import tensorflow as tf
import nltk
from nltk.corpus import wordnet as wn
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.tree import ParentedTree, Tree

from itertools import groupby
from stanfordcorenlp import StanfordCoreNLP
#from tool import filter
import chatbot.crawler as crawler
import chatbot.deeplearning as deep
import chatbot.kdddatabased as kb
from settings import PROJECT_ROOT
from chatbot.botpredictor import BotPredictor

class ChatBot:
    """
        Intelligent dialogue model based on-
        1. Template-based- AIML
        2. Knowledge Based- MySQL \\\
        3. Web Search
        4. Deep Learning: RNN
    """
    
    # initialize
    colorama.init()
    ws.load()
    #nltk.download()
    
    def __init__(self, config_file='config.cfg', host='http://localhost', port=9000):
        config = configparser.ConfigParser()
        config.read(config_file)
        self.filter_file = config.get('resource', 'filter_file')
        self.load_file = config.get('resource', 'load_file')
        self.save_file = config.get('resource', 'save_file')
        self.shelve_file = config.get('resource', 'shelve_file')
                
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
        
        #Initialization learning library
        self.template = '<aiml version="1.0" encoding="UTF-8">\n{rule}\n</aiml>'
        self.category_template = '<category><pattern>{pattern}</pattern><template>{answer}</template></category>'
    
        # Initialize Filter sensitive words
        #self.gfw = filter.DFAFilter()
        #self.gfw.parse(self.filter_file)
    
        # Use an existing server: StanfordCoreNLP
        self.nlp = StanfordCoreNLP(host, port=port, timeout=30000)
        self.props = {
            'annotators': 'tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation',
            'pipelineLanguage': 'en',
            'outputFormat': 'json'
        }
        
        # Initialize the Language Tool for GEC 
        self.tool = language_check.LanguageTool('en-US')
        

################################################################

    def response(self, user_message):
        print('# User -->: '+user_message)
        
        # Limit word count
        if len(user_message) > 100:
            return self.mybot.respond('MAX')
        elif len(user_message) == 0:
            return self.mybot.respond('MIN')
        
        # Filter sensitive words
        #message = self.gfw.filter(message, "*")
        #if message.find("*") != -1:
            #return self.mybot.respond('FILTER')
            
        # Grammar Error Check and Prompt to User
        gec_message = self.checkGrammarError(user_message)
        print('Correction -->: '+gec_message)
        matches = self.tool.check(user_message)
        if(len(matches)>0):
            return self.mybot.respond('Confirmation '+ gec_message)
        
        # Start Conversation
        responseAnswer = ''
        botresponse = self.mybot.respond(gec_message)
        print ('# Bot1  --> ' + botresponse)
        
        if botresponse[0]=='@':            
            botresponse = botresponse.replace('@','')
            botresponse = self.mybot.respond(botresponse)
            print('2222--> '+botresponse)
        
        # Initialize Lemmatization
        wordnet_lemmatizer = WordNetLemmatizer()
        
        # User Sentence Tokenization
        word_tokens = self.nlp.word_tokenize(botresponse)
        
        # Removing stopwords
        stop_words = set(stopwords.words('english')) 
        #stopwords.extend(string.punctuation)
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
        
        #print(colorama.Fore.GREEN+'\n********************* Dependency Parser ********************* '+colorama.Fore.RESET) 
        #dependency_parser = self.nlp.dependency_parse(' '.join(final_sentence))
        #print(dependency_parser)
        
        # POS Tagger
        postagger = self.nlp.pos_tag(' '.join(final_sentence))
        print(colorama.Fore.YELLOW+'\n------------------ Identify POS Tagger -------------------------- '+colorama.Fore.RESET)
        print('pos tagger: ', postagger)
            
        print("-----------------------------------------------------------------------")
        grammar = r"""Chunk: {<RB.?>*<VB.?>*<NNP>+<NN>?}"""
        cp = nltk.RegexpParser(grammar)
        #tree = cp.parse(postagger)
        #print ("CP: ", cp)
        tree = cp.parse(postagger)
        print (tree)           
        
        for word, pos in postagger:
            if pos=='NNP':
                print (word)
        print("-----------------------------------------------------------------------")
        #https://github.com/ayat-rashad/ayat-rashad.github.io/blob/master/triples.ipynb
        
        
        # Add all NOUNs into list
        nounEntityList = [] 
        for pos in postagger:
            if pos[1] in ('NN','NNS','NNP','NNPS'):
                nounEntityList.append(pos[0])
        print(colorama.Fore.GREEN+'\n------------------ Added NOUN into Entity List ------------------------- '+colorama.Fore.RESET)        
        print(nounEntityList, '\n')
            
            
        # 1: Template-based Strategy
        if botresponse[0] != '#':
            print('Template-based Strategy')
            responseAnswer = botresponse
        
        # 2: KB Searching Strategy
        elif botresponse.find('#NONE#') != -1:
            print('KB Searching Strategy')
            nounEntityList.remove('#NONE')
            ans = ''
            ans = kb.kdd_search(nounEntityList, ' '.join(final_sentence), gec_message)
            if ans != '':
                responseAnswer = ans.encode('utf-8')
            
            # 3: Internet Retrieval Strategy
            else:
                print('Internet Retrieval Strategy')
                #ans = crawler.web_search(gec_user_message)
                
                if ans != '':
                    responseAnswer = ans.encode('utf-8')
                    
                # 4: Generative Strategy- RNN
                else:
                    print('Generative Strategy')
                    ans = deep.neural_network(self, gec_message)
                    responseAnswer = ans.encode('utf-8')                    
        
        # 5: Learning Mode
        elif result.find('#LEARN#') != -1:
            question = result[8:]
            answer = message
            self.save(question, answer)
            return self.mybot.respond('Already studied')
        
        else:
            responseAnswer = self.mybot.respond('I don\'t know.')
            
        return responseAnswer 
    
    
    # Grammar Error Check on Raw User Input
    def checkGrammarError(self, user_message):
        print(colorama.Fore.GREEN+'\n------------------ Grammar Error Correction -------------------------- '+colorama.Fore.RESET)
        matches = self.tool.check(user_message)
        gec_user_message = language_check.correct(user_message, matches)
        if(len(matches)>0):
            i = 0 
            for x in matches:
                print('Grammatical Error --> ', matches[i])
                print('Apply Rules--> ', matches[i].replacements)
                i=i+1            
        else:
            print('No Error Found.')        
        return gec_user_message
        
    
    # SAVE Model
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
        bot.response(user_message)
