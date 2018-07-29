import requests
import os
from urllib.request import urlretrieve

'''
函数说明：下载《王者荣耀盒子》中的英雄图片

Parameters:
    heros_url - GET请求地址，通过Fiddler抓包获取
    header - header信息
Returns:
    无
Author:
    启航
Blog:

Modify:
    2018-07-01
'''


def hero_imgs_download(heros_url, header):
    response = requests.get(url=heros_url, headers=header).json()
    print(response)
    hero_num = len(response['list'])
    print('一共有{}个英雄'.format(hero_num))
    hero_images_path = 'hero_images'
    for each_hero in response['list']:
        hero_photo_url = each_hero['cover']
        hero_name = each_hero['name'] + '.jpg'
        filename = hero_images_path + '/' + hero_name
        if hero_images_path not in os.listdir():
            os.makedirs(hero_images_path)
        urlretrieve(url=hero_photo_url, filename=filename)


if __name__ == '__main__':
    headers = {'Accept-Charset': 'UTF-8',
            'Accept-Encoding': 'gzip,deflate',
            'Content-type': 'application/x-www-form-urlencoded',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 6.0; M5s Build/MRA58K)',
            'Host': 'gamehelper.gm825.com',
            'Connection': 'Keep-Alive'}
    heros_url = 'http://gamehelper.gm825.com/wzry/hero/list?channel_id=90001a&app_id=h9044j&game_id=7622&game_name=%E7%8E%8B%E8%80%85%E8%8D%A3%E8%80%80&vcode=13.0.1.0&version_code=13010&cuid=760FAE2D09C58F5E35DBAECFDCE5A54C&ovr=6.0&device=Meizu_M5s&net_type=1&client_id=YjFT%2FEFzWS%2Bi9JhIkBlZhg%3D%3D&info_ms=Ken42c%2FWDaEQ7Ha0LfxI1A%3D%3D&info_ma=dVi7JDaux7ObPIBusHmNKadYITFbU%2Bzugx%2F0fdxEC80%3D&mno=0&info_la=GE1LMQNGfjm4CHxbK9MaGw%3D%3D&info_ci=GE1LMQNGfjm4CHxbK9MaGw%3D%3D&mcc=0&clientversion=13.0.1.0&bssid=TlYfPofADXLhD5RJnitO5FTSFdWbHJtMmY1HYE4hrSI%3D&os_level=23&os_id=c2b007a4beef53c3&resolution=720_1280&dpi=320&client_ip=192.168.1.107&pdunid=612QZCQS2242F'
    hero_imgs_download(heros_url, headers)
