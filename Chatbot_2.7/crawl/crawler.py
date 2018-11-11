
from search import *

#####################
#     Search Web    #
#####################
def search(message):
    result = ''
    
    '''Wikipedia'''
    ### Need to Identify Entity before search from Wiki
    if message.find('einstein') != -1:
        result += get_wikipedia('einstein')
        result+= '\n'
        result += 'You can get more information at https://www.britannica.com/biography/Albert-Einstein'
        return result
    
        
    '''Joke'''
    if message.find('joke') != -1:
        result += 'Ok, here is a joke for you~~~\n'
        result += get_joke()
        return result

    return result


if __name__ == '__main__':
    message = "RazChatbot"
    print search(message)
