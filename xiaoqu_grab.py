# pip3 install lxml -i https://pypi.tuna.tsinghua.edu.cn/simple/
# pip3 install beautifulsoup4 -i https://pypi.tuna.tsinghua.edu.cn/simple/
# pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple/
# nohup python3 runner.py > shanghai.log 2>&1 &
# tail -500f shanghai.log
# wc -l sh.csv

import vars
import util
import json
from lxml import etree
from bs4 import BeautifulSoup

TOWNS = []
# 保存当前断点信息
CUR_OFFSET = ["zhiwuyuan"]


# 初始化城市下的数据
def init_city_data(city):
    data = util.read_json("config/{0}.json".format(city), mode="r")
    list = []
    for area in data:
        for town in area["l"]:
            if town["e"] not in list:
                list.append(town["e"])
    return list


# 开始执行
def start(url, town):
    util.logging.info("开始执行{0}-------------".format(town))
    text = parse_xiaoqu_list(url, town)
    page = parse_xiaoqu_page(text)
    if len(page) > 0:
        for i in range(page[0], page[1], 1):
            url = vars.URL_TEMPLATE3.format(vars.CITY, vars.TYPE, town, i)
            util.logging.info("解析第{0}页**************".format(i))
            parse_xiaoqu_list(url, town)
    util.logging.info("执行{0}结束-------------".format(town))


# 解析小区列表，主执行流程
def parse_xiaoqu_list(url, town):
    response = util.http_get(url)
    # 获取小区的url列表
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", class_="listContent")
    if ul != None:
        list = ul.find_all("li", class_="clear xiaoquListItem")
        length = len(list)
        util.logging.info("当前页共{0}个小区".format(length))
        # 按页读取并写入csv
        data = []
        for li in list:
            url = li.find("a", class_="img")["href"]
            sell_count = (
                li.find("div", class_="xiaoquListItemSellCount")
                .find("a")
                .find("span")
                .text
            )
            trans_count = li.find("div", class_="houseInfo").find_all("a")[0].text
            hire_count = li.find("div", class_="houseInfo").find_all("a")[1].text
            util.logging.info("开始抓取，{0}".format(url))
            row = parse_xiaoqu_detail(url, town, sell_count, trans_count, hire_count)
            data.append(row)
        if len(data) > 0:
            util.write_csv("out/{0}.csv".format(vars.CITY), "a", data)
            util.logging.info("共写入{0}条数据".format(len(data)))
    return response.text


# 解析小区详情页面
def parse_xiaoqu_detail(url, town, sell_count, trans_count, hire_count):
    response = util.http_get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    name = soup.find("h1", class_="detailTitle").text
    adds = soup.find("div", class_="detailDesc").text
    price = 0
    if soup.find("span", class_="xiaoquUnitPrice") != None:
        price = soup.find("span", class_="xiaoquUnitPrice").text
    # content
    content = soup.find_all("span", class_="xiaoquInfoContent")
    build_type = content[0].text
    house_count = content[1].text
    floor_count = content[2].text
    green_rate = content[3].text
    plot_rate = content[4].text
    trans_type = content[5].text
    build_year = content[6].text
    supply_heating = content[7].text
    supply_water = content[8].text
    supply_electric = content[9].text
    # outer
    outers = soup.find_all("span", class_="xiaoquInfoContent outer")
    property_fee = outers[0].text
    xiaoqu = ""
    mendian = ""
    nearby = ""
    if outers[1].find("span", class_="actshowMap") != None:
        xiaoqu = outers[1].find("span", class_="actshowMap")["xiaoqu"]
        mendian = outers[1].find("span", class_="actshowMap")["mendian"]
        span = outers[1].find("span", class_="actshowMap").text
        nearby = span + outers[1].text
    property_company = outers[2].text
    developer = outers[3].text

    return [
        town,
        name,
        adds,
        price,
        sell_count,
        trans_count,
        hire_count,
        build_type,
        house_count,
        floor_count,
        green_rate,
        plot_rate,
        trans_type,
        build_year,
        supply_heating,
        supply_water,
        supply_electric,
        property_fee,
        xiaoqu,
        mendian,
        nearby,
        property_company,
        developer,
        url,
    ]


# 解析小区列表翻页


def parse_xiaoqu_page(text):
    # 解析列表翻页的total和curPage
    soup = BeautifulSoup(text, "html.parser")
    div = soup.find("div", class_="page-box house-lst-page-box")
    if div != None and div["page-data"]:
        page_data = json.loads(div["page-data"])
        cur = page_data["curPage"]
        total = page_data["totalPage"]
        util.logging.info("共{0}页，当前第{1}页".format(total, cur))
        return [cur, total]
    else:
        return []


if __name__ == "__main__":
    TOWNS = init_city_data(vars.CITY)
    util.logging.info("初始化数据完成，共{0}条数据".format(len(TOWNS)))
    # 从断点处继续执行
    town_pos = TOWNS.index(CUR_OFFSET[0]) if len(CUR_OFFSET) > 0 else 0
    util.logging.info("从{0}继续抓取".format(TOWNS[town_pos]))

    for town in TOWNS[town_pos:]:
        url = vars.URL_TEMPLATE2.format(vars.CITY, vars.TYPE, town)
        start(url, town)
