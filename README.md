
### Installation 
pip install -r requirements.txt

$ pip install jieba
$ pip install aiml
$ pip install lxml
$ pip install beautifulsoup4
$ pip install flask


### Running Server  
Working directory: chatbot_2.7/core
```
$ cd chatbot_2.7/core
$ python web/server.py (nohub)

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

Step 3: Internet Search (WebQA)
News----Sina News
Article----A daily article
Jokes----Anecdote
Time----Sogou time
Weather----Sogou weather
Air----Sogou Air
If the search does not find answer, go to step four.

Step 4: Neural Network
The next-generation dialogue engine based on the Seq2Seq model not only trains the best answer in the existing answer, but can create a human-like answer. 

Dataset:
https://drive.google.com/file/d/1mVWFScBHFeA7oVxQzWb8QbKfTi3TToUr/view


