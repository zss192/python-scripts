#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import time
import jieba  
import random
import threading
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt 
from bs4 import BeautifulSoup           
from PIL import Image
from os import path
from wordcloud import WordCloud 
from fake_useragent import UserAgent

total_title=[]  #总的搜索结果的标题，用于词频分析
total_info=[]   #总的搜索结果信息
ua = UserAgent(verify_ssl=False)

# 词频百分比统计
def count(count_list,count_nums):
    '''
    Args:
        count_list:待分析词列表
        count_sum:统计词数目
    '''

    counts = {}
    sum=0   #字数不为1的词总个数
    for word in count_list:
        if(len(word) == 1 or word=="..." or word=="视频" or word=="会员" or word=="知乎"):  #去除字数为1的词和省略号
            continue
        counts[word] = counts.get(word,0) + 1
        sum+=1
    items = list(counts.items())
    items.sort(key=lambda x:x[1], reverse=True) 
    print("----前十高频词汇百分比如下----")
    for i in range(count_nums):
        word, count = items[i]
        print("{0:\u3000<10}{1:>10.3%}".format(word, count/sum))

# 绘画词云图
def draw(draw_list):
    '''
    Args:
        draw_list:待绘画词列表
    '''

    text = " ".join(draw_list)

    # 结巴分词
    jieba.setLogLevel(20) # 不打印日志
    cut_text= jieba.lcut(text)
    result= "/".join(cut_text)

    # 调用词频统计函数
    count(cut_text,10)

    # 不显示的词组
    exclude={"视频","会员","知乎"}

    # 设置词云图属性
    wc = WordCloud(font_path=r"SimSun.ttf",background_color='white',max_font_size=90,
                max_words=1000,width=600,height=400,stopwords=exclude) #mask=backImage
    wc.generate(result)
    
    # 显示图片
    plt.figure("视频类会员搜索结果分析")
    plt.imshow(wc)      
    plt.axis("off")     
    plt.show()

# 根据百度会的加密的Url得到真正的URL
def convert_url(url):
    '''
    Args:
        url:网址链接
    '''
    resp = requests.get(url=url,
                        headers=headers,
                        allow_redirects=False
                        )
    return resp.headers['Location']

# get请求抓取搜索结果信息
def getInfo(pages):
    '''
    Args:
        pages:搜索的页数
    '''
    total_url=[]
    total_abstract=[]
    temp_title=[]   # 临时存放该页面抓取到的标题
    global total_info
    global total_title

    s = requests.session()
    url = 'https://www.baidu.com/s'
    params = {
        "wd": wd,
        "pn": pages,
    }
    headers={
                'User-Agent':ua.Firefox, 
                'Referer': "www.baidu.com",
            } 
    r = s.get(url=url, headers=headers, params=params)
    soup = BeautifulSoup(r.text, 'lxml')
    for so in soup.select('#content_left .result'):
        g_url = convert_url(so.a.get('href'))#对界面获取的url进行进行访问获取真实Url
        g_title=so.a.get_text().replace('\n','').strip()#根据分析标题无对应标签 只能获取标签内文字 去掉换行和空格  
        try: 
            #去除视频等特殊情况
            g_abstract=so.find('div', class_='c-abstract').get_text().replace('\n','').strip()
        except:
            print(g_url)
        total_title +=[g_title]
        temp_title +=[g_title]
        total_url +=[g_url]
        total_abstract +=[g_abstract]
    # 用zip函数汇总搜索信息
    total_info+=zip(temp_title,total_url,total_abstract)

# 获取搜索结果信息  
def search_info(wd,num):
    '''
    Args:
        wd:搜索内容
        num:搜索总页数
    '''

    global total_info
    global total_title

    print("----开始抓取搜索结果----")

    # 每个线程抓取一个页面的结果
    thread_list = []
    for i in range(num):
        t = threading.Thread(target=getInfo,args=(i*10,))
        thread_list.append(t)

    for t in thread_list:
        t.setDaemon(True)
        t.start()

    for t in thread_list:
        t.join()

    print("----抓取搜索结果结束----")
            
    try:
        df=pd.DataFrame(data=total_info,columns=['标题','URL','摘要'])
        df.to_csv(r'search_baidu_data.csv',index=False,encoding='utf_8_sig')
        print("保存搜索结果信息到search_data.csv文件成功")
    except:
        return 'FALSE'

    # 调用draw函数绘画词云图
    draw(total_title)
    
if __name__ == '__main__':

    # 随机伪造header头
    headers={
                'User-Agent':ua.Firefox, 
                'Referer': "www.baidu.com",
            } 
    wd = "视频类会员价格"    # 搜索内容
    num = 50           # 总结果信息数目约等于num*10
    search_info(wd,num)
