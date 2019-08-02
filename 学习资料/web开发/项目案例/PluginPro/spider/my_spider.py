import time

import requests

url = "http://127.0.0.1:5000/"

# 模拟浏览器
headers = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0"
}

for i in range(1000):
    res = requests.get(url, headers=headers)
    print(res.text)
    time.sleep(0.1)


