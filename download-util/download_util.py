import os.path
import time
from random import randint
import requests
from bs4 import BeautifulSoup

"""
mainly use for download novels on 笔趣阁
"""


def download(baseurl, dest):

    """
    MAIN FUNCTION
    INPUT: baseurl, 准备下载的小说的目录页，如神印王座的目录页为:https://www.mayiwxw.com/9_9558/
           dest: 下载到的本地地址，如下载到本地地址为:D:\\novel_source\\Throne of Seal\\
    """

    host = 'https://www.mayiwxw.com'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) '
                             'Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,'
                         'application/signed-exchange;v=b3;q=0.9',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
               'Connection': 'keep-alive',
               'Referer': 'https://www.mayiwxw.com/',
               'sec-ch-ua': '" Not;A Brand";v="99", "Microsoft Edge";v="103", "Chromium";v="103"',
               }
    url_strings, name, src, file_cnt = get_download_urls(baseurl, headers, dest)
    i = file_cnt
    print(f'----------开始下载{name}全部章节，共{len(url_strings)}章----------')
    for url_string in url_strings:
        i += 1  # 计数
        url = f'{host}{url_string}'  # 转化为url
        content, title = get_download_contents(url, headers, i)
        chapter = change_contents_style(content, i)
        write_into_local(chapter, title, dest, i)
    write_book_img(host, headers, name, src, dest)
    print(f"----------{name}全部共{i}章节已下载完毕，本地地址为：{dest}----------")


def get_download_urls(baseurl, headers, dest):
    print("----------开始获取全部章节地址----------")
    res = requests.get(baseurl, headers=headers)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    url_list = soup.find('div', id='list').find('dl')
    urls = url_list.find_all('a')
    url_strings = []

    # 获得正文dt到前一个dt的超链接数量
    all_tag = url_list.find_all(True, recursive=False)
    tag_names = []
    for tag in all_tag:
        tag_names.append(tag.name)

    cnt = 0
    num = 0
    for name in tag_names:
        if name == 'dt' and cnt == 0:
            cnt += 1
            num = 0
        elif name == 'dt' and cnt == 1:
            break
        else:
            num += 1

    for url in urls:
        url_strings.append(url['href'])

    # 获得文件夹里已经下载的章节数量
    files = os.listdir(dest)
    file_cnt = len(files)
    num += file_cnt
    if file_cnt != 0:
        print(f'----------已经下载{file_cnt}章内容，继续下载其余章节----------')

    url_strings = url_strings[num:]  # 删去最新章节的几个超链接

    # 封面图片
    book_img = soup.find('div', id='fmimg').find('img')
    src = book_img['src']

    print('----------已经获取全部章节地址----------')
    name = soup.find('div', id='info').find('h1').text
    return url_strings, name, src, file_cnt


def get_download_contents(url_string, headers, i):
    res = requests.get(url_string, headers=headers)
    # print(res.text)
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    content = soup.find('div', id='content')
    title = soup.find('div', class_='bookname').find('h1').text
    print(f'----------已经爬取第{i}页内容----------', end='\n')
    time.sleep(5 + randint(1, 5))
    return content, title


def change_contents_style(content, i):
    chapter = str(content)
    chapter = chapter.replace('<br/>', '\n').removeprefix('<div id="content"><div '
                                                          'id="center_tip"><b>最新网址：www.mayiwxw.com</b></div>') \
        .removesuffix('<div id="center_tip"><b>最新网址：www.mayiwxw.com</b></div></div>').replace('(《》)', '')
    print(f'----------已经转换第{i}章内容----------', end='\n')
    return chapter


def write_into_local(chapter, title, dest, i):
    if not os.path.exists(dest):
        os.mkdir(dest)
    if title == "":
        title = "未获得的title-" + str(i)
    title = title.replace('\\', '').replace('/', '').replace('*', '').replace('?', '').replace("\"", '')\
        .replace('<', '').replace('>', '').replace('|', '')
    file = dest + title + '.txt'
    f = open(file, 'w', encoding='utf-8')
    f.write(chapter)
    print(f'----------已经写入第{i}章内容至本地----------', end='\n')


def write_book_img(host, headers, name, src, dest):
    img_url = f'{host}{src}'
    img = requests.get(img_url, headers=headers)
    file = f'{dest}{name}.jpg'
    with open(file, 'wb') as f:
        f.write(img.content)
