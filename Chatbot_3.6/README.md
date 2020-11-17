# IntelliBot Demo 
AI Based chatbot using Python, AIML, Angular and Bootstrap 

### Requirements

    Python >= 3.5x
    AIML >= 0.9
	Flask
	Lxml
	Beautifulsoup4
	Jieba
	Tensorflow 1.2 
	MySQL 5.5 
	
### Installation

1. Clone and navigate to chatbot directory.

2. Install the required packages. 
    ```bash 
    $ pip install -r requirements.txt
  
3. You're done, chat with your IntelliBot :)


### Run in the browser 

    $ cd Medius_Chatbot/core
	$ python web/server.py
	
	> ......
	> * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)


### Run in Command Prompt (CMD)  

    $ cd chatbot_3.6
	$ python web\server.py  
	
	> Kernel bootstrap completed
	> User > 
	> ......
	> * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)

###Processing flow
Step 1: Pretreatment
Limit word count
Filter sensitive words (disgusting, political, pornographic, illegal...)

Step 2: Knowledge Base Matching (AIML)
Basic functions: say hello, gossip...
Exception handling: the problem is too long, a blank question, no response can be found...
Emotional answer: expression, praise, ridicule...
If the match does not match, go to step three.

Step 3: Internet Searching
Article----A daily article
Jokes----Anecdote
Weather----weather
If the search does not find answer, go to step four.

Step 4: Neural Network
The next-generation dialogue engine based on the Seq2Seq model not only trains the best answer in the existing answer, but can create a human-like answer. 

Original Cornell Dataset: [cleaned it using Python script] 
http://www.cs.cornell.edu/~cristian/Cornell_Movie-Dialogs_Corpus.html

Reddit Dataset:
https://www.reddit.com/r/datasets/comments/3bxlg7/i_have_every_publicly_available_reddit_comment/

Pre-trained Dataset:
https://drive.google.com/file/d/1mVWFScBHFeA7oVxQzWb8QbKfTi3TToUr/view

Standford NLP
https://stanfordnlp.github.io/CoreNLP/


### Screenshot 
   ![alt tag](https://github.com/nuruzzaman/Medius_Chatbot/blob/master/screenshot/chatbot_screen_1.PNG) 


### Author

***[Mohammad Nuruzzaman, PhD](https://github.com/nuruzzaman/)***  
University of New South Wales, Australia.  
Currently working as a Data Scientist at ELMO Software Ltd. 


### Additional Resources 
	python -m nltk.downloader punkt
	python -m nltk.downloader stopwords
	import nltk
	nltk.download('wordnet')
	tensorboard --logdir Data\Result\
	java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
	SET PASSWORD FOR 'root'@'localhost' = PASSWORD('soho1234');
