import logging
import requests
import json
import random
import time
import csv
import util
import vars

# 配置日志输出格式
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


# get请求
def http_get(url):
    delay = random.uniform(vars.DELAY_CONF["min"], vars.DELAY_CONF["max"])
    logging.info("{0}秒后执行".format(delay))
    time.sleep(delay)
    try:
        headers = {
            # "Upgrade-Insecure-Requests":"1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Connection": "close",
        }
        respones = requests.get(url, headers=headers, timeout=20)
    except requests.exceptions.Timeout:
        util.logging.error("请求超时，请检查网络连接或增加超时时间")
        return None
    except requests.exceptions.RequestException as e:
        util.logging.error("请求异常:", e)
        return None
    return respones


# 写入json文件，mode=w:write，mode=r:read，mode=a:append
def write_json(path, mode, data):
    # encoding='utf-8-sig'为UTF-8 with BOM格式，可以使用excel打开
    with open(path, mode, encoding="utf-8-sig") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


# 读json文件
def read_json(path, mode):
    with open(path, mode, encoding="utf-8-sig") as file:
        return json.load(file)


# 读csv文件
def read_csv(path, mode):
    data = []
    with open(path, mode, encoding="utf-8-sig") as file:
        reader = csv.reader(file)
        for row in reader:
            data.append(row)
    return data


# 写csv文件
def write_csv(path, mode, data):
    with open(path, mode, newline="", encoding="utf-8-sig") as file:
        writer = csv.writer(file)
        writer.writerows(data)
