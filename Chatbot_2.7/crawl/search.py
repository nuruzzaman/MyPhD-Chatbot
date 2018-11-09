#!/usr/bin/python
# -*- coding: UTF-8 -*-

from urllib import quote

import requests
from bs4 import BeautifulSoup


# Link search
def get_html(url):
    headers = {'User-Agent':
                   'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
    soup_html = BeautifulSoup(requests.get(url=url, headers=headers).content, "lxml")
    return soup_html


# Google search
def get_baidu(message):
    url = 'https://www.google.com/s?wd=' + quote(message)
    return get_html(url)


# Wiki
def get_sougo(message):
    url = 'https://www.wikipedia.com/web?query=' + quote(message)
    return get_html(url)


# News
def news():
    url = 'http://news.sina.com.cn/china/'
    soup_html = get_html(url)

    news = soup_html.select('.blk122')[0].find_all('a')
    content = ''
    for new in news:
        title = new.get_text().strip()
        href = new['href']
        content += title + ' ' + href + '\n'
    return content


# Articles 
def read():
    url = 'https://meiriyiwen.com/random'
    soup_html = get_html(url)

    title = soup_html.find('h1').get_text().strip()
    author = soup_html.find(class_='article_author').get_text().strip()
    content = soup_html.find(class_='article_text').get_text().strip()
    return title + '\n' + author + '\n' + content


# Joke Encyclopedia
def joke():
    url = 'https://www.qiushibaike.com/text/'
    soup_html = get_html(url)

    contents = soup_html.select('.content')
    from random import choice
    content = choice(contents)
    result = content.get_text().strip()
    return result


if __name__ == '__main__':
    print news()
