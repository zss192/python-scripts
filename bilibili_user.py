#!/usr/bin/env python3
import os
import requests
import time
import threading
import pandas as pd
import datetime
from fake_useragent import UserAgent

total_info=[]
ua = UserAgent(use_cache_server=False)
ua = UserAgent(verify_ssl=False)

# 获取一个线程所爬取的个人用户信息
def get_UserInfo(mid,thread_num):
    """
    Args:
        mid: 用户ID
        thread_num：一个线程爬取的id数量
    """
    global total_info
    for i in range(thread_num):
        user_info=[]
        url = 'https://api.bilibili.com/x/space/acc/info?mid='+str(mid+i)
        # 随机伪造header头
        headers={
                    'User-Agent':ua.Chrome, 
                }
        req = requests.get(url, headers=headers)
        if req.status_code == 200:
            status = req.json()
            if status.get('data'):
                data = status['data']
                result = {
                    'mid': data['mid'],
                    'name': data['name'],
                    'sex': data['sex'],
                    'vipType' : data['vip']['label']['text'],
                    'vipStatus' : '是' if data['vip']['status']==1 else '否',
                    'level': data['level']
                }
                userStr=str(result['mid'])+'#'+result['name']+'#'+result['sex']+'#'+str(result['level'])+'#'+result['vipStatus']+'#'+str(result['vipType'])           
                user_info=userStr.split('#')
                total_info.append(user_info)
        else:
            print('获取用户个人信息失败,code {}'.format(req.status_code))
            print(url)      
    time.sleep(1.1)

# 爬取设定数量id的总的用户信息
def main(thread_num,start,stop):
    """
    Args:
        thread_num：一个线程爬取的id数量
        start:起始id
        stop:结束id
    """
    thread_list = []   
    for i in range(start,stop,thread_num):
        t = threading.Thread(target=get_UserInfo,args=(i,thread_num))
        thread_list.append(t)

    for t in thread_list:
        t.setDaemon(True)
        t.start()

    for t in thread_list:
        t.join()

    if total_info:
        # 对用户信息按id排序
        total_info.sort(key=lambda x: x[0])

        df=pd.DataFrame(data=total_info,columns=['用户ID','昵称','性别','等级','是否为VIP','vip种类'])
        today=datetime.datetime.today()
        
        # 如果文件存在就追加不添加表头
        if not os.path.exists('bilibili_data_'+str(today)[5:10]+'.csv'):
            df.to_csv(r'bilibili_data_'+str(today)[5:10]+'.csv', mode='a',index=False,encoding='utf_8_sig')
        else:
            df.to_csv(r'bilibili_data_'+str(today)[5:10]+'.csv', mode='a',index=False,encoding='utf_8_sig',header=False)
        
        print("爬取id为"+str(start)+"---"+str(stop))
        print("保存用户信息到bilibili_data_"+str(today)[5:10]+'.csv成功')
    else:
        print("爬取信息为空!")

if __name__ == '__main__':
    main(20,1959000,1960000)
