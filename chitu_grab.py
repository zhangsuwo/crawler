import logging
import json
import random
import time
import util
import csv

URL_TEMPLATE4 = "https://{0}.lianjia.com/{1}/{2}/rs{4}/"


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


if __name__ == "__main__":
    data = load_data("out/chitu.csv")
    print(len(data))
