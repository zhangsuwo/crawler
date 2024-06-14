import util
import csv
from bs4 import BeautifulSoup


def load_data(path):
    data = []
    with open(path, newline="") as file:
        reader = csv.reader(file)
        for row in reader:
            id = row[0]
            name = row[3]
            city = "gz"
            area = "baiyun"
            data.append([id, name, city, area])
    return data


def search_xiaoqu_info():
    response = util.http_get("https://gz.lianjia.com/xiaoqu/rs东信华庭/")
    soup = BeautifulSoup(response.text, "html.parser")
    ul = soup.find("ul", class_="listContent")
    if ul == None:
        return ""
    list = ul.find_all("li", class_="clear xiaoquListItem")
    length = len(list)
    util.logging.info("当前页共{0}个小区".format(length))
    for li in list:
        url = li.find("a", class_="img")["href"]
        sell_count = (
            li.find("div", class_="xiaoquListItemSellCount").find("a").find("span").text
        )
        trans_count = li.find("div", class_="houseInfo").find_all("a")[0].text
        hire_count = li.find("div", class_="houseInfo").find_all("a")[1].text
        print(url)
        print(sell_count)
        print(trans_count)
        print(hire_count)


if __name__ == "__main__":
    search_xiaoqu_info()
