# nohup python3 chitu_run.py > log/chitu_run.log 2>&1 &
# tail -500f log/chitu_run.log
# wc -l out/chitu_out.csv
# tar -czvf config.tar.gz config

import util
import xiaoqu_run
import vars
from bs4 import BeautifulSoup

# 保存当前断点信息
CUR_OFFSET = ["SQ00015480"]


def search_xiaoqu_info(city,url):
    row = []
    util.logging.info("开始查询小区信息：{0}".format(url))
    response = util.http_get(url)
    if response == None:
        util.logging.info("查询地址：{0}，查询结果为NULL".format(url))
        return row
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("div", class_="houseList")
    if ul == None:
        return row
    list = ul.find_all("div", class_="rel")
    # 默认取结果列表的第一个
    if list == None or len(list) <= 0:
        return row
    util.logging.info("查询结果共{0}个小区".format(len(list)))
    li = list[0]
    href = vars.URL_TEMPLATE2.format(city) + li.find("dl").find("dt").find("a")['href']
    util.logging.info("开始查询第一个小区详情：{0}".format(href))
    uls = li.find("dl").find("dd").find("ul")
    if uls == None or len(uls) <= 0:
      return row
    type = li.find("dl").find("dd").find("p").find("span").text
    sell_count = uls.find_all('li')[0].find('a').text
    hire_count = uls.find_all('li')[1].find('a').text
    util.logging.info("类型为{0}".format(type))
    if type == "住宅" or type == "别墅":
      row = xiaoqu_run.parse_xiaoqu_detail(href, type, sell_count, 0, hire_count)
      util.logging.info("数据为{0}".format(row))
    return row

if __name__ == "__main__":
    rows = util.read_csv("out/chitu.csv", mode="r")
    util.logging.info("初始化数据完成，共{0}条数据".format(len(rows)))
    row_pos = 0
    if len(CUR_OFFSET) > 0:
        for i in range(0, len(rows), 1):
            if rows[i][0] == CUR_OFFSET[0]:
                row_pos = i
    util.logging.info("从{0}位置继续抓取".format(row_pos))

    for row in rows[row_pos:]:
        id = row[0]
        if len(row[4]) <= 0 and row[12] == "ftx":
          href = row[2]
          name = row[3]
          if len(href) > 0 and len(name) > 0:
            city = href.split('.')[0].split("//")[1]
            url = vars.URL_TEMPLATE1.format(city, name)
            info = search_xiaoqu_info(city,url)
            if len(info) > 0:
              row[4] = info["name"] if 'name' in info.keys() else ""
              row[5] = info["adds"] if 'adds' in info.keys() else ""
              row[6] = info["price"] if 'price' in info.keys() else ""
              row[7] = info["floor_count"] if 'floor_count' in info.keys() else ""
              row[8] = info["house_count"] if 'house_count' in info.keys() else ""
              row[9] = info["build_year"] if 'build_year' in info.keys() else ""
              row[10] = "UNKOWN"
              row[11] = info["property_company"] if 'property_company' in info.keys() else ""
        util.write_csv("out/chitu_out.csv", mode="a", data=[row])
        util.logging.info("写入{0}数据成功".format(id))