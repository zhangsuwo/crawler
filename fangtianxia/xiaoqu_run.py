# pip3 install lxml -i https://pypi.tuna.tsinghua.edu.cn/simple/
# pip3 install beautifulsoup4 -i https://pypi.tuna.tsinghua.edu.cn/simple/
# pip3 install requests -i https://pypi.tuna.tsinghua.edu.cn/simple/
# nohup python3 xiaoqu_run.py > log/xiaoqu_run.log 2>&1 &
# tail -500f log/xiaoqu_run.log
# wc -l out/bj.csv

import vars
import util
import json
from bs4 import BeautifulSoup

# 保存当前断点信息
CUR_OFFSET = ["darushijia"]


# 初始化城市下的数据
def init_city_data(city):
    data = util.read_json("config/{0}.json".format(city), mode="r")
    list = []
    for area in data:
        for town in area["list"]:
            if town["py"] not in list:
                list.append(town["py"])
    return list


# 解析一个镇
def parse_town(url, town):
    util.logging.info("开始执行{0}-------------".format(town))
    text = parse_xiaoqu_list(url, town)
    page = parse_xiaoqu_page(text)
    if len(page) <= 0:
        return
    for i in range(page[0], page[1], 1):
        url = vars.URL_TEMPLATE3.format(vars.CITY, vars.TYPE, town, i)
        util.logging.info("解析第{0}页，{1}".format(i, url))
        parse_xiaoqu_list(url, town)
    util.logging.info("执行{0}结束-------------".format(town))


# 解析小区列表，主执行流程
def parse_xiaoqu_list(url, town):
    response = util.http_get(url)
    if response == None:
        return ""
    # 获取小区的url列表
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", class_="listContent")
    if ul == None:
        return ""

    list = ul.find_all("li", class_="clear xiaoquListItem")
    length = len(list)
    util.logging.info("当前页{0},共{1}个小区".format(url, length))
    # 按页读取并写入csv
    data = []
    for li in list:
        url = li.find("a", class_="img")["href"]
        sell_count = (
            li.find("div", class_="xiaoquListItemSellCount").find("a").find("span").text
        )
        trans_count = li.find("div", class_="houseInfo").find_all("a")[0].text
        hire_count = li.find("div", class_="houseInfo").find_all("a")[1].text
        util.logging.info("开始抓取明细页信息，{0}".format(url))
        row = parse_xiaoqu_detail(url, town, sell_count, trans_count, hire_count)
        if len(row) > 0:
            data.append(row)
    if len(data) > 0:
        util.write_csv("out/{0}.csv".format(vars.CITY), "a", data)
        util.logging.info("本页共写入{0}条数据".format(len(data)))
    return response.text


# 解析小区详情页面
def parse_xiaoqu_detail(url, type, sell_count, trans_count, hire_count):
    data = {}
    response = util.http_get(url)
    if response == None:
        return data
    soup = BeautifulSoup(response.text, "html.parser")
    title_div = soup.find('div',class_='title_village clearfix')
    if title_div == None:
        util.logging.info("未找到title_div")
        return data
    data["name"] = title_div.find("h3").text
    data["score"] = title_div.find('a',class_="link_grade").text

    info_div = soup.find('div',class_='info_village_r')
    if info_div == None:
        util.logging.info("未找到info_div")
        return data
    price_div = info_div.find('div',class_='price_village clearfix')
    if price_div == None:
      data["price"] = "UNKOWN"
    else:
      data["price"] = price_div.find('p').find('b').text

    content = info_div.find('div',"village_info").find("ul").find_all('li')
    for li in content:
        # if li.find('span').text == "二手房源":
        #   data["esf_count"] = li.find('p').find("a").text
        # if li.find('span').text == "特价房源":
        #   data["spec_count"] = li.find('p').find("a").text
        if li.find('span').text == "楼栋总数":
          if li.find('p').find('a') != None:
            data["floor_count"] = li.find('p').find('a').text
          else:
            data["floor_count"] = li.find('p').text
        if li.find('span').text == "房屋总数":
          if li.find('p').find('a') != None:
            data["house_count"] = li.find('p').find('a').text
          else:
            data["house_count"] = li.find('p').text
        # if li.find('span').text == "建筑类型":
        #   data["build_type"] = li.find('p').text
        if li.find('span').text == "建筑年代":
          if li.find('p').find('a') != None:
            data["build_year"] = li.find('p').find('a').text
          else:
            data["build_year"] = li.find('p').text
        if li.find('span').text == "小区位置":
            data["adds"] = li.find('p').find('span').text
        if li.find('span').text == "物业公司":
          if li.find('p').find('a') != None:
            data["property_company"] = li.find('p').find('a').text.strip()
          else:
            data["property_company"] = li.find('p').text.strip()
        # if li.find('span').text == "开发商":
        #   data["developer"] = li.find('p').find('a').text.strip()

    return data

# 解析小区列表翻页
def parse_xiaoqu_page(text):
    data = []
    # 解析列表翻页的total和curPage
    soup = BeautifulSoup(text, "html.parser")
    div = soup.find("div", class_="page-box house-lst-page-box")
    if div != None and div["page-data"]:
        page_data = json.loads(div["page-data"])
        cur = page_data["curPage"]
        total = page_data["totalPage"]
        util.logging.info("共{0}页，当前第{1}页".format(total, cur))
        data.append(cur)
        data.append(total)
    return data


if __name__ == "__main__":
    data = init_city_data(vars.CITY)
    util.logging.info("初始化数据完成，共{0}条数据".format(len(data)))
    # 从断点处继续执行
    town_pos = data.index(CUR_OFFSET[0]) if len(CUR_OFFSET) > 0 else 0
    util.logging.info("从{0}继续抓取".format(data[town_pos]))

    for town in data[town_pos:]:
        url = vars.URL_TEMPLATE2.format(vars.CITY, vars.TYPE, town)
        parse_town(url, town)
