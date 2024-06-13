# nohup python3 config_grab.py > config_grab.log 2>&1 &

import util
import vars
from bs4 import BeautifulSoup


# 获取省市列表
def get_city_list():
    response = util.http_get(vars.CITY_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    list = soup.find_all("li", class_="city_list_li city_list_li_selected")
    data = []
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
    response = util.http_get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # 查找ershoufang下第1个div
    div = soup.find("div", attrs={"data-role": "ershoufang"}).find_all("div")[0]
    list = div.find_all("a")
    data = []
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
    response = util.http_get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    # 查找ershoufang下第2个div
    div = soup.find("div", attrs={"data-role": "ershoufang"}).find_all("div")[1]
    list = div.find_all("a")
    data = []
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
    for prov in data:
        util.logging.info("当前省份为：{0}".format(prov["name"]))
        for city in prov["list"]:
            util.logging.info("当前城市为：{0}".format(city["py"]))
            areas = get_area_list(city, vars.TYPE)
            util.logging.info("抓取{0}完成,共{1}条数据".format(city["py"], len(areas)))
            util.write_json("config/{0}.json".format(city["py"]), data=areas, mode="w")
            util.logging.info(
                "写入文件config/{0}.json完成,共{1}条数据".format(city["py"], len(areas))
            )
