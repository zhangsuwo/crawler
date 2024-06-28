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
        # 修改市字段
        city_name = row[5][0:-1]
        # 修改小区字段step1，替换包含城市的词语
        xiaoqu_name = row[3].replace(city_name, "")
        # 去掉小区名称中多余字符
        x = xiaoqu_name.find('（')
        y = xiaoqu_name.find('）')
        if x > -1 and y > -1:
          sub_str = xiaoqu_name[x:y+1]
          xiaoqu_name = xiaoqu_name.replace(sub_str,"")
        # step2
        a = xiaoqu_name.find('【')
        b = xiaoqu_name.find('】')
        if a > -1 and b > -1:
          sub_str = xiaoqu_name[a:b+1]
          xiaoqu_name = xiaoqu_name.replace(sub_str,"")
        # step3
        c = xiaoqu_name.find('·')
        if c > -1:
          xiaoqu_name = xiaoqu_name.split('·')[-1].replace(city_name,"")
    
        city_url = ""
        for city in cities:
            if city_name == city["name"]:
                city_url = city["href"]
        row.append(city_name)
        row.append(city_url)
        row.append(xiaoqu_name)
    util.write_csv("out/chitu.csv", "w", data)


if __name__ == "__main__":
    format_data()
