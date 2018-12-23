import os
from hashlib import md5
from multiprocessing.pool import Pool
from urllib.parse import urlencode

import requests

headers = {
        "user-agent": "Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 69.0.3497.100Safari / 537.36",
        "cookie": 'tt_webid=6591674770407851527; UM_distinctid=16555dd135182a-0aaf457dfee96f-2711938-144000-16555dd13525c0; csrftoken=e874c1c4c92de13796f658055b321509; tt_webid=6591674770407851527; WEATHER_CITY=%E5%8C%97%E4%BA%AC; uuid="w:69e07afc4113469c8a67bc7e1191a8fe"; ccid=5b05c00c464a23364e612a873a8f8bf8; CNZZDATA1259612802=1586168555-1534743351-%7C1539254542; __tasessionId=y296rn1i01539258641108',
        "x-requested-with": "XMLHttpRequest",
    }

# 获取网页返回的结果
def get_page(offset):
    params = {
        'offset': offset,
        'format': 'json',
        'keyword': '街拍',
        'autoload': 'true',
        'count': '20',
        'cur_tab': '1',
        'from': 'search_tab'
    }
    base_url = 'https://www.toutiao.com/search_content/?'
    url = base_url + urlencode(params)
    try:
        resp = requests.get(url,headers=headers)
        if resp.status_code == 200:
            return resp.json()
    except requests.ConnectionError:
        return None

# 获取图片
def get_images(json):
    if json.get('data'):
        data = json.get('data')
        for item in data:
            if item.get('cell_type') is not None:
                continue
            title = item.get('title')
            images = item.get('image_list')
            for image in images:
                yield {
                    'image': 'https:' + image.get('url'),
                    'title': title
                }

# 保存图片至指定路径
def save_image(item):
    img_path = 'D:/imagedata/{title}/'.format(title=item.get('title'))
    if not os.path.exists(img_path):
        os.makedirs(img_path)
    try:
        pic = requests.get(item.get('image'))
        if pic.status_code == 200:
            file_path = img_path + '{file_name}.jpg'.format(
                file_name=md5(pic.content).hexdigest())
            if not os.path.exists(file_path):
                with open(file_path, 'wb') as f:
                    f.write(pic.content)
                print('%s Save Successful' % file_path)
            else:
                print('Already Downloaded', file_path)
    except requests.ConnectionError:
        print('Failed to Save Image，item %s' % item)

# 主函数
def main(offset):
    json = get_page(offset)
    for item in get_images(json):
        print(item)
        save_image(item)


GROUP_START = 0
GROUP_END = 20

if __name__ == '__main__':
    pool = Pool()
    groups = ([x * 20 for x in range(GROUP_START, GROUP_END + 1)])
    pool.map(main, groups)
    pool.close()
    pool.join()
