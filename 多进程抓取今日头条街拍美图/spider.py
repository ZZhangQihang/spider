import os
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
import json
import pymongo
from hashlib import md5
from config import *
from multiprocessing import Pool
from json.decoder import JSONDecodeError

client = pymongo.MongoClient(MONGO_URL, connect=False)
db = client[MONGO_DB]

'''
函数说明：获取页面html

Parameters:
    offset 
    keyword - 关键字
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-06-15
'''
def get_page_index(offset, keyword):
    data = {
        'offset': offset,
        'format': 'json',
        'keyword': keyword,
        'autoload': 'true',
        'count': '20',
        'cur_tab': 1,
        'from': 'search_tab'
    }
    url = 'https://www.toutiao.com/search_content/?' + urlencode(data)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求索引页出错')
        return None
'''
函数说明：解析页面html

Parameters:
    html 
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-06-15
'''


def parse_page_index(html):
    try:
        data = json.loads(html)
        if data and 'data' in data.keys():
            for item in data.get('data'):
                if item.get('article_url'):
                    yield item.get('article_url')
    except JSONDecodeError:
        pass
'''
函数说明：获取详情页html

Parameters:
    url -详情页url
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-06-15
'''


def get_page_detail(url):
    headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print('请求详情页出错', url)
        return None
'''
函数说明：解析详情页html

Parameters:
    html -详情页html
    url -详情页url
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-06-15
'''


def parse_page_detail(html, url):
    soup = BeautifulSoup(html, 'lxml')
    title = soup.select('title')[0].get_text()
    print(title)
    images_pattern = re.compile('gallery: JSON.parse\("(.*?)"\),', re.S)
    result = re.search(images_pattern, html)
    if result:
        data = json.loads(result.group(1).replace('\\', ''))
        if data and 'sub_images' in data.keys():
            sub_images = data.get('sub_images')
            images = [item.get('url')for item in sub_images]
            for image in images:download_image(image)
            return {
                'title': title,
                'url': url,
                'images': images,
            }
'''
函数说明：保存数据库

Parameters:
    result -解析后数据
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-06-15
'''


def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print('存储到MongoDB成功', result)
        return True
    return False
'''
函数说明：下载图片

Parameters:
    url -图片url
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-06-15
'''


def download_image(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    }
    print('正在下载', url)
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            save_image(response.content)
        return None
    except RequestException:
        print('请求图片出错', url)
        return None
'''
函数说明：保存图片

Parameters:
    content 
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-06-15
'''


def save_image(content):
    file_path = '{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    if not os.path.exists(file_path):
        with open(file_path, 'wb') as f:
            f.write(content)
            f.close()
'''
函数说明：主函数

Parameters:
    offset
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-06-15
'''

def main(offset):
    html = get_page_index(offset, KEYWORD)
    for url in parse_page_index(html):
        html = get_page_detail(url)
        if html:
            result = parse_page_detail(html, url)
            if result: save_to_mongo(result)


if __name__ == '__main__':
    groups = [x*20 for x in range(GROUP_START, GROUP_END+1)]
    pool = Pool()
    pool.map(main, groups)