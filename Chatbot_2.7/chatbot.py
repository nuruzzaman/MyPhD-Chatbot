import ConfigParser
import shelve
import aiml
import wordsegment as ws

import crawler
import deeplearning

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
        self.load_file = config.get('resource', 'load_file')
        self.save_file = config.get('resource', 'save_file')
        self.shelve_file = config.get('resource', 'shelve_file')
        self.filter_file = config.get('resource', 'filter_file')

        # initialize
        ws.load()
        
        # Initialize the knowledge base
        self.mybot = aiml.Kernel()
        self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')
        
        # Initialize the template-based learning 
        self.template = '<aiml version="1.0" encoding="UTF-8">\n{rule}\n</aiml>'
        self.category_template = '<category><pattern>{pattern}</pattern><template>{answer}</template></category>'

    def response(self, message):
        # Limit word count
        if len(message) > 100:
            return self.mybot.respond('MAX')
        elif len(message) == 0:
            return self.mybot.respond('MIN')    
        
        # End chat
        if message == 'exit' or message == 'quit':
            return self.mybot.respond('Thank you for using Chatbot. Good Bye')         
        
        # Start chatting
        else:
            result = self.mybot.respond(' '.join(ws.segment(message)))
            
            # Template-based mode
            if result[0] != '#':
                print 'Template-based mode--> ' + result
                return result
            
            elif result.find('#NONE#') != -1:
                # KB Searching mode  #
                ######################
                print 'Database Searching mode--> ' + result
                ans = ''
                #ans = database.search(message)
                if ans != '':
                    return ans.encode('utf-8')
                else: 
                    # WEB Searching mode #
                    ######################
                    print 'Web Searching mode--> ' + result
                    ans = crawler.search(message)
                    if ans != '':
                        return ans.encode('utf-8')
                    else:
                        # DEEP Learing- RNN #
                        #####################
                        print 'Neural Network mode--> ' + result
                        ans = deeplearning.rnn_generator(message)
                        return ans.encode('utf-8')
            
            # Self-Learning Mode
            elif result.find('#LEARN#') != -1:
                print 'Learning Mode--> ' + result
                question = result[8:]
                answer = message
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
        import os
        os.remove(self.save_file) if os.path.exists(self.save_file) else None
        os.remove(self.shelve_file) if os.path.exists(self.shelve_file) else None
        self.mybot.bootstrap(learnFiles=self.load_file, commands='load aiml b')


if __name__ == '__main__':
    bot = ChatBot()	
    while True:		
        message = raw_input('User > ')
        print 'Bot > ' + bot.response(message)
