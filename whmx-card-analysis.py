import requests
import qrcode as qr
import time
import json

url = "https://goda.srap.link/qrcode_login"
check_url = "https://goda.srap.link/check_qrcode"

headers = {
    'User-Agent': 'Apifox/1.0.0 (https://apifox.com)',
    'Accept': '*/*',
    'Host': 'goda.srap.link',
    'Connection': 'keep-alive',
    'Cookie': 'sl-session=TXTgBgnZvmaetoutYaz9WA=='
}

def get_chouka_data():
    response = requests.request("POST", url, headers=headers)
    
    if response.status_code == 200:
        qrcode_data = response.json()['data']
        # 将字典转换为字符串
        qrcode = "biligame://portal/auth/login/qrcode?" + qrcode_data            
        # 将二维码转换为图片
        img = qr.make(qrcode)
        img.save("qrcode.png")
        
        # 打开二维码图片
        img.show()
        
        payload1 = {
            "ticket": str(qrcode_data)
        }
        
        # 等待扫码
        response_qrcode = None
        while not response_qrcode or  response_qrcode.json()['status']==False:
            # 轮询检查扫码状态
            response_qrcode = requests.post(check_url, headers=headers,json=payload1)
            time.sleep(1)  # 每隔2秒检查一次
        # 扫码成功
        
        access_key, uid = response_qrcode.json()['data']['access_key'], response_qrcode.json()['data']['uid']
        pages = 1
        data = []
        while True:
            # 轮询获取游戏数据
            
            payload2 = {
                    "code": str(access_key),
                    "uid": str(uid),
                    "page": pages,
                    "pagesize": 10,
                    "type": [
                    "time"
                ],
                }
            # 获取游戏数据
            get_game_data = requests.post("https://goda.srap.link/getDrawCardHistory", headers=headers, json=payload2)
            if "false" in get_game_data.text:
                # 已经获取完所有游戏数据
                print("已经获取完所有数据，等待整合...")
                return data
            time.sleep(1)  # 每隔1秒获取一次
            # 获取游戏数据成功
            data.append(str(get_game_data.text))
            print("获取到{}页数据".format(pages))
            pages += 1
    else:
        print("获取登录二维码失败")
        return None, None
    
    
def data_analysis(data):
    print("开始分析数据...")
        # 分析数据
    import json
    list_data = []
    # 假设你的嵌套JSON数据如下
    for i in range(len(data)):
        json_data = data[i]

        game_data = json.loads(json_data)
        for item in game_data['data']:
            list_data.append([item["CardName"], item["Rare"], item["PoolName"]])
        # poolnames = [item['PoolName'] for item in game_data['data']]
        # cardnames = [item['CardName'] for item in game_data['data']]
        # rares = [item['Rare'] for item in game_data['data']]
        # print(poolnames, cardnames, rares)
    print("分析完成")
    # 打印分析结果

    print("游戏数据如下：")

    techu, youyi, xinsheng = 0, 0, 0
    for i in range(len(list_data)):
        if list_data[i][1] == 4:
            techu += 1
    print("特出器者:",techu)
    for i in range(len(list_data)):
        if list_data[i][1] == 3:
            youyi += 1
    print("优异器者:",youyi)
    for i in range(len(list_data)):
        if list_data[i][1] == 2:
            xinsheng += 1
    print("新生器者:",xinsheng)
    #详细卡池数据：
    while True:
        accu = input("输入y查看详细卡池数据，输入s结束程序：")
        if accu == "y":
            print("详细卡池数据如下：")
            for i in range(len(list_data)):
                print(list_data[i])
        elif accu == "s":
            exit()
        else:
            print("输入错误，请重新输入")
if __name__ == '__main__':
    data_analysis(get_chouka_data())