import util as util
import vars

HEADER = [
    "名称",
    "区镇",
    "地址",
    "单价",
    "建筑类型",
    "房屋总数",
    "楼栋总数",
    "交易权属",
    "建成年代",
    "物业费",
    "物业公司",
    "开发商",
]


def format_data(path, out_path):
    data = [HEADER]
    list = util.read_csv(path, "r")
    util.logging.info("共读取{0}条数据".format(len(list)))
    for row in list:
        name = row[1]
        adds_array = row[2][1:].split(")")
        town = adds_array[0]
        adds = adds_array[1]
        price = row[3]
        build_type = row[7]
        house_count = row[8]
        floor_count = row[9]
        trans_type = row[12]
        build_year = row[13]
        property_fee = row[17]
        property_company = row[21]
        developer = row[22]
        data.append(
            [
                name,
                town,
                adds,
                price,
                build_type,
                house_count,
                floor_count,
                trans_type,
                build_year,
                property_fee,
                property_company,
                developer,
            ]
        )
    if len(data) > 0:
        util.logging.info("共{0}条数据格式化".format(len(data)))
        util.write_csv(out_path, "a", data)


if __name__ == "__main__":
    src = "out\{0}.csv".format(vars.CITY)
    target = "out\{0}_out.csv".format(vars.CITY)
    format_data(src, target)
