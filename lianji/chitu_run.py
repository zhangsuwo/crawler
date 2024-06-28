# nohup python3 chitu_run.py > log/chitu_run.log 2>&1 &
# tail -500f log/chitu_run.log
# wc -l out/chitu_out.csv
# tar -czvf config.tar.gz config

import utils.util as util
import xiaoqu_run
from bs4 import BeautifulSoup

# 保存当前断点信息
CUR_OFFSET = ["SQ00139790"]


def search_xiaoqu_info(url):
    row = []
    util.logging.info("开始查询小区信息：{0}".format(url))
    response = util.http_get(url)
    if response == None:
        util.logging.info("查询地址：{0}，查询结果为NULL".format(url))
        return row
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", class_="listContent")
    if ul == None:
        return row
    list = ul.find_all("li", class_="clear xiaoquListItem")
    # 默认取结果列表的第一个
    if list == None or len(list) <= 0:
        return row
    util.logging.info("查询结果共{0}个小区".format(len(list)))
    li = list[0]
    href = li.find("a", class_="img")["href"]
    util.logging.info("开始查询第一个小区详情：{0}".format(href))
    sell_count = (
        li.find("div", class_="xiaoquListItemSellCount").find("a").find("span").text
    )
    trans_count = li.find("div", class_="houseInfo").find_all("a")[0].text
    hire_count = li.find("div", class_="houseInfo").find_all("a")[1].text
    row = xiaoqu_run.parse_xiaoqu_detail(href, "", sell_count, trans_count, hire_count)
    return row


if __name__ == "__main__":
    data = util.read_csv("out/chitu.csv", mode="r")
    header = data[0]
    rows = data[1:]
    util.logging.info("初始化数据完成，共{0}条数据".format(len(rows)))
    row_pos = 0
    if len(CUR_OFFSET) > 0:
        for i in range(0, len(rows), 1):
            if rows[i][0] == CUR_OFFSET[0]:
                row_pos = i
    util.logging.info("从{0}位置继续抓取".format(row_pos))

    for row in rows[row_pos:]:
        id = row[0]
        if len(row) > 15:
            href = row[15]
            name = row[16]
            if len(href) > 0 and len(name) > 0:
                url = "{0}/xiaoqu/rs{1}".format(href, name)
                info = search_xiaoqu_info(url)
                if len(info) > 0:
                    row.append(info[1])
                    row.append(info[2])
                    row.append(info[3])
                    row.append(info[8])
                    row.append(info[9])
                    row.append(info[13])
                    row.append(info[17])
                    row.append(info[21])
        util.write_csv("out/chitu_out.csv", mode="a", data=[row])
        util.logging.info("写入{0}数据成功".format(id))
