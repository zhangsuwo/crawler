import util

# 对chitu原始数据格式化
def format_data():
    data = util.read_csv("out/chitu.csv", mode="r")
    util.logging.info("共读取{0}条chitu数据".format(len(data)))
    list = util.read_json("config/cities.json", mode="r")
    util.logging.info("共读取{0}条省数据".format(len(list)))

    cities = []
    for item in list:
        for city in item["list"]:
            cities.append(city)
    util.logging.info("共{0}个城市".format(len(cities)))

    for row in data:
      if row[4] == "" or row[2] == "":
        row.append("ftx")
        for city in cities:
          if row[1] == city["name"]:
            row[2] = city["href"]
      else:
        row.append("lianjia")
    util.write_csv("out/chitu.csv", "w", data)


if __name__ == "__main__":
    format_data()
