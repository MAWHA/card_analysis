from requests import post
import qrcode
import time
from colorama import init,Fore,Back,Style


class get_userinfo():
    '''
    获取用户用于登录的access_key和uid
    '''
    def __init__(self,):
        '''
        初始化
        '''
        self.url = "https://goda.srap.link/qrcode_login"
        self.check_url = "https://goda.srap.link/check_qrcode"
        self.card_info_url = "https://goda.srap.link/getDrawCardHistory"
        self.headers = {
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Accept': '*/*',
    'Host': 'goda.srap.link',
    'Connection': 'keep-alive',
}    
        
    def get_qrcode(self):
        '''
        获取二维码,返回ticket
        '''
        data = post(self.url, headers=self.headers)
        if data.json()['status'] != True:
            print("获取用户信息失败")
        data = data.json()
        qrcode_data = data.get('data')
        user_info_url = "biligame://portal/auth/login/qrcode?" + qrcode_data
        img = qrcode.make(user_info_url)
        img.show()
        self.qrcode_data = qrcode_data
        return qrcode_data

    def check_qrcode(self,qrcode_data):
        payload = {
            "ticket": str(qrcode_data)
        }
        response_qrcode = None
        while not response_qrcode or  response_qrcode.json()['status']==False:
            response_qrcode = post(self.check_url, headers=self.headers,json=payload)
            time.sleep(1)
        self.account_info = response_qrcode.json()['data']
    
    def get_account_info(self):
        access_key = self.account_info.get('access_key')
        uid = self.account_info.get('uid')
        return access_key, uid

    def get_card_info(self,access_key,uid):
        pages = 1
        card_info = None
        card_info_list = []
        while card_info == None or card_info.json().get('message')!="发生错误":
            payload = {
                    "code": str(access_key),
                    "uid": str(uid),
                    "page": pages,
                    "pagesize": 10,
                    "type": [
                    "time"
                ],
                }
            card_info = post(self.card_info_url, headers=self.headers,json=payload)
            if card_info.json().get('data') != []: 
                card_info_list.append(card_info.json().get('data'))
                print(f"获取到第{pages}页数据")
                pages += 1
        return card_info_list
    

class card_analysis():
    '''
    分析卡池信息
    继承自get_userinfo类
    '''
    def analysis_card_info(self,card_info_list):
        techu, youyi, xinsheng = 0,0,0
        CardName_list = []
        for card_info in card_info_list:
            for i in card_info:
                card_name = i.get('CardName')
                rare = i.get('Rare')
                if rare == 4:
                    CardName_list.append(card_name)
                    techu += 1
                elif rare == 3:
                    youyi += 1
                elif rare == 2:
                    xinsheng += 1
        print("\033[32m抽卡总数:{}\033[0m".format(techu+youyi+xinsheng))
        print("\033[32m出红概率:{:.2f}%\033[0m".format(float(techu/(techu+youyi+xinsheng))*100))

        print(f"\033[31m特出器者:{techu}\033[0m",end=" ")
        for i in CardName_list:
            print(f"\033[31m{i}\033[0m",end=" ")
        print(f"\033[33m\n优异器者:{youyi}\033[0m")
        print(f"\033[34m新生器者:{xinsheng}\033[0m")

    def all_card_info(self,card_info_list):
        '''
        打印所有卡池信息
        '''
        all_card_info = []
        for card_info in card_info_list:
            for i in card_info:
                pool_name = i.get('PoolName')
                card_name = i.get('CardName')
                rare = i.get('Rare')
                all_card_info.append(f"卡池:{pool_name},器者:{card_name},稀有度:{rare}")
                
        return all_card_info
if __name__ == '__main__':
    user_info = get_userinfo()

    qrcode_data = user_info.get_qrcode()
    user_info.check_qrcode(qrcode_data=qrcode_data)
    access_key, uid = user_info.get_account_info()
    card_info_list = user_info.get_card_info(access_key,uid)

    card_analysis = card_analysis()
    card_analysis.analysis_card_info(card_info_list)

    user_input = None
    while user_input ==None or user_input not in ['e']:
        user_input = input("输入y查看所有卡池信息,输入s保存卡池信息到目录下card_info.txt文件,输入e退出:")
        if user_input == 'y':
            print(f"卡池信息如下:",end='\n')
            for card_info in card_info_list:
                for i in card_info:
                    pool_name = i.get('PoolName')
                    card_name = i.get('CardName')
                    rare = i.get('Rare')
                    if rare == 4:
                        print(f"\033[31m卡池:{pool_name},器者:{card_name},稀有度:{rare}\033[0m")
                    elif rare == 3:
                        print(f"\033[33m卡池:{pool_name},器者:{card_name},稀有度:{rare}\033[0m")
                    elif rare == 2:
                        print(f"\033[34m卡池:{pool_name},器者:{card_name},稀有度:{rare}\033[0m")
        elif user_input =='s':
            with open('card_info.txt','w',encoding='utf-8') as f:
                f.write("查询时间:{}".format(time.strftime('%Y-%m-%d %H:%M:%S'),end='\n'))
                card_data = card_analysis.all_card_info(card_info_list)
                for card_info in card_data:
                    f.write(str(card_info))
                    f.write('\n')
            print("卡池信息保存成功")

