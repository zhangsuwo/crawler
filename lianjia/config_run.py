# nohup python3 config_run.py > log/config_run.log 2>&1 &
# tail -500f log/config_run.log
# tar -czvf config.tar.gz config

import util as util
import vars
from bs4 import BeautifulSoup

# 保存当前断点信息
CUR_OFFSET = ["重庆", "cq"]


# 获取省市列表
def get_city_list():
    data = []
    response = util.http_get(vars.CITY_URL)
    if response == None:
        return data
    soup = BeautifulSoup(response.text, "html.parser")
    list = soup.find_all("li", class_="city_list_li city_list_li_selected")
    for li in list:
        c = li.find("div", "city_firstletter").find("span").text
        provs = li.find("div", "city_list").find_all("div", "city_province")
        for prov in provs:
            prov_name = prov.find("div", "city_list_tit c_b").text
            cities = prov.find("ul").find_all("li")
            item = {"c": c, "prov": prov_name, "list": []}
            for city in cities:
                href = city.find("a")["href"]
                name = city.find("a").text
                py = href.split("//")[1].split(".")[0]
                item["list"].append({"href": href, "name": name, "py": py})
            data.append(item)
    return data


# 获取城市下的区列表
def get_area_list(city, type):
    url = city["href"] + type
    util.logging.info("获取区列表的url为：{0}".format(url))

    data = []
    response = util.http_get(url)
    if response == None:
        return data

    soup = BeautifulSoup(response.text, "html.parser")
    # 可能不存在ershoufang的div
    ershoufang = soup.find("div", attrs={"data-role": "ershoufang"})
    if ershoufang == None:
        return data
    # 查找ershoufang下第1个div
    divs = ershoufang.find_all("div")
    if divs == None:
        return data
    div = divs[0]
    list = div.find_all("a")
    for a in list:
        name = a.text.strip()
        py = a["href"][1:-1].split("/")[1].strip()
        towns = get_town_list(city["py"], type, py)
        data.append({"name": name, "py": py, "list": towns})
    return data


# 获取区下的镇列表
def get_town_list(city, type, area):
    url = vars.URL_TEMPLATE2.format(city, type, area)
    util.logging.info("获取镇列表的url为：{0}".format(url))

    data = []
    response = util.http_get(url)
    if response == None:
        return data

    soup = BeautifulSoup(response.text, "html.parser")
    ershoufang = soup.find("div", attrs={"data-role": "ershoufang"})
    if ershoufang == None:
        return data
    # 查找ershoufang下第2个div
    divs = ershoufang.find_all("div")
    if divs == None or len(divs) <= 1:
        return data
    div = divs[1]
    list = div.find_all("a")
    for a in list:
        name = a.text.strip()
        py = a["href"][1:-1].split("/")[1].strip()
        data.append({"name": name, "py": py})
    return data


if __name__ == "__main__":
    # data = get_city_list()
    # util.write_json('config/cities.json',mode="w",data=data)
    # util.logging.info("写入文件config/cities.json完成,共{0}条数据".format(len(data)))
    data = util.read_json("config/cities.json", "r")
    prov_pos = 0
    city_pos = 0
    for i in range(0, len(data), 1):
        prov = data[i]
        if CUR_OFFSET[0] != "" and prov["prov"] == CUR_OFFSET[0]:
            prov_pos = i
            for j in range(0, len(prov["list"]), 1):
                city = prov["list"][j]
                if CUR_OFFSET[1] != "" and city["py"] == CUR_OFFSET[1]:
                    city_pos = j

    for prov in data[prov_pos:]:
        util.logging.info("当前省份为：{0}".format(prov["prov"]))
        for city in prov["list"][city_pos:]:
            util.logging.info("当前城市为：{0}".format(city["py"]))
            areas = get_area_list(city, vars.TYPE)
            util.logging.info("抓取{0}完成,共{1}条数据".format(city["py"], len(areas)))
            util.write_json("config/{0}.json".format(city["py"]), data=areas, mode="w")
            util.logging.info(
                "写入文件config/{0}.json完成,共{1}条数据".format(city["py"], len(areas))
            )
