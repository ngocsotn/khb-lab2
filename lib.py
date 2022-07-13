import json
from os import path, makedirs
import time
import statistics
# from random import randint

count_item = 0
in_use = False

def get_full_file_path(file_path):
    return path.abspath(file_path)

def check_exist(file_path):
    return path.exists(file_path)

def create_folder(folder_path):
    if not check_exist(folder_path):
        makedirs(folder_path)

def generate_json_item():
    return {
        "number": "",
        "name": "",
        "price": "",
        "price_sale": "",
        "discount_percent": "",
        "sold_count":"",
        "url":"",
        "platform": "",
        "picture":[],
        "category":[],
        "point": "",
        "mall": False,
        "ship": ""
    }

def replace_data_json(new_data, filename, json_title):
    global in_use

    if not in_use:
        in_use = True
        with open(filename, 'r+', encoding='utf-8') as file:
            file_data = json.load(file)
            file_data[json_title] = new_data
            file.seek(0)
            json.dump(file_data, file, indent = 4, ensure_ascii=False)
            time.sleep(0.01)
            in_use = False

def append_into_arr_in_json(new_data_json, filename, array_name):
    global in_use
    if not in_use:
        in_use = True
        with open(filename, 'r+', encoding='utf-8') as file:
            file_data = json.load(file)
            file_data[array_name].append(new_data_json)
            file.seek(0)
            json.dump(file_data, file, indent = 4, ensure_ascii=False)
            time.sleep(0.01)
            in_use = False
    
def read_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        file_data = json.load(file)
        return file_data

def write_json(new_data_json, filename):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump(new_data_json, file, indent = 4, ensure_ascii=False)

def isIntOrFloat(int_num):
    return int_num.replace('.','',1).isdigit()
                
def tst():
    json_data = read_json("records/05-09-2021_00.11.04.json")
    print(len(json_data["data"]))

def cleanPriceAndDiscount(data):
    data = data.replace('₫','')
    data = data.replace('%','')
    while("." in data):
        data = data.replace('.','')
    return data

def filterData():
    json_data = read_json("records/05-09-2021_00.11.04.json")
    json_data_2 = read_json("records/07-10-2021_19.30.46.json")
    new_json_data = { "count" : 0} #len(json_data["data"]) + len(json_data_2["data"])
    data = []
    final_data = []
    data.extend(json_data["data"])
    data.extend(json_data_2["data"])
    i = 1
    for item in data:
        item["number"] = i
        new_json_data["count"] = i
        i += 1

        if isIntOrFloat(str(item["point"])):
            item["point"] = float(item["point"])
        else:
            item["point"] = 0

        item["price"] = cleanPriceAndDiscount(item["price"])
        if isIntOrFloat(str(item["price"])):
            item["price"] = int(float(item["price"]))
        else:
            item["price"] = 0
        
        item["price_sale"] = cleanPriceAndDiscount(item["price_sale"])
        if isIntOrFloat(str(item["price_sale"])):
            item["price_sale"] = int(float(item["price_sale"]))
        else:
            item["price_sale"] = 0

        if isIntOrFloat(str(item["sold_count"])):
            item["sold_count"] = int(float(item["sold_count"]))
        else:
            item["sold_count"] = 0

        item["discount_percent"] = str(item["discount_percent"])
        item["discount_percent"] = cleanPriceAndDiscount(item["discount_percent"])

        if item["discount_percent"] != "":
           
            if isIntOrFloat(item["discount_percent"]):
                item["discount_percent"] = int(float(item["discount_percent"]))
            else:
                item["discount_percent"] = 0
            
            # case 1, discount không phải số, và 2 giá đang > 100
            if item["discount_percent"] == 0 and item["price"] > 100 and item["price_sale"] > 100:
                if item["price"] < item["price_sale"]:
                    item["price"], item["price_sale"] = item["price_sale"], item["price"]
                    item["discount_percent"] = int((item["price"]-item["price_sale"])*100/item["price"])

            # case 2: bộ 3 %, giá, giá sale đảo lộn
            if item["discount_percent"] > 100 or item["price"] == 0 or item["price_sale"] == 0:
                number_arr = [item["price_sale"], item["discount_percent"], item["price"]]
                number_arr.sort()
                item["price"] = number_arr[2]
                item["price_sale"] = number_arr[1]
                if item["price_sale"] == 0:
                    item["price_sale"] = item["price"]
                item["discount_percent"] = int((item["price"]-item["price_sale"])*100/item["price"])
        else:
            item["discount_percent"] = 0

        if len(item["category"]) > 0:
            if "quốc tế" in item["category"][0].lower():
                item["category"].pop(0)
            final_data.append(item)
    

    new_json_data["data"] = final_data
    write_json(new_json_data, "filtered/data_fresh.json")

# xóa các outliner
def deleteOutliner():
    json_data = read_json("filtered/data_fresh.json")
    new_json_data = { "count" : 0}
    data = []
    i = 1
    for item in json_data["data"]:
        if len(item["category"]) != 0 and float(item["point"]) > 0.0 and item["price"] > 0:
            item["number"] = i
            i +=1
            data.append(item)
    new_json_data["count"] = i
    new_json_data["data"] = data
    write_json(new_json_data, "filtered/data.json")

# viết lại các outliner nào có thể viết = giá trị trung bình
def rewriteOutliner():
    json_data = read_json("filtered/data_fresh.json")
    new_json_data = { "count" : 0}
    data = []
    i = 1
    avg_point = statistics.mean([i["point"] for i in json_data["data"]])
    avg_price = statistics.mean([i["price"] for i in json_data["data"]])
    for item in json_data["data"]:
        if len(item["category"]):
            if float(item["point"]) == 0.0:
                item["point"] = avg_point
            if item["price"] == 0:
                item["price"] = avg_price
            item["number"] = i
            i +=1
            data.append(item)
    new_json_data["count"] = i
    new_json_data["data"] = data
    write_json(new_json_data, "filtered/data_rewrite.json")

# filterData()
# deleteOutliner()
rewriteOutliner()