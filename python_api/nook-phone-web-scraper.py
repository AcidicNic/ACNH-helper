from flask import Flask, jsonify, request
from lxml import html
import requests
import re
import json

app = Flask(__name__)


@app.route('/getAllVillagers', methods=['GET'])
def get_all_villagers():
    data = get_villagers()
    return jsonify({'villagers': data})

# @app.route('/getVillagerData/<str:name>', methods=['GET'])
# def get_villager_data(name):
#     return jsonify({'data': villager_lookup(name)})


def get_villagers():
    url = "https://nookipedia.com/w/api.php?action=query&list=categorymembers&cmtitle=Category:New_Horizons_characters&cmlimit=max&format=json"
    raw_villagers = requests.get(url).json()["query"]["categorymembers"]
    villagers = []
    for v in raw_villagers:
        try:
            img_data = requests.get(f"https://nookipedia.com/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:{v['title']}_NLa.png&format=json").json()["query"]["pages"]
            img_url = img_data[list(img_data.keys())[0]]["imageinfo"][0]["url"]
        except:
            img_url = None
        villagers.append({
            "name": v['title'],
            "img_url": img_url,
            "data": villager_lookup(v['title'])
        })
    return villagers


def get_critters():
    bug_url = "https://nookipedia.com/w/api.php?action=query&list=categorymembers&cmtitle=Category:New_Horizons_bugs&cmlimit=max&format=json"
    fish_url = "https://nookipedia.com/w/api.php?action=query&list=categorymembers&cmtitle=Category:New_Horizons_fish&cmlimit=max&format=json"
    raw_bugs = requests.get(bug_url).json()["query"]["categorymembers"]
    raw_fish = requests.get(fish_url).json()["query"]["categorymembers"]

    critters = {
        "bugs": [],
        "fish": []
    }

    for b in raw_bugs:
        try:
            img_data = requests.get(f'https://nookipedia.com/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:{b["title"]}.jpg&format=json').json()["query"]["pages"]
            img_url = img_data[list(img_data.keys())[0]]["imageinfo"][0]["url"]
        except:
            img_url = None
        critters["bugs"].append({
            "name": b['title'],
            "img_url": img_url,
            "data": critter_lookup(b['title'], 'bug')
        })

    for f in raw_fish:
        try:
            img_data = requests.get(f'https://nookipedia.com/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:{f["title"]}.jpg&format=json').json()["query"]["pages"]
            img_url = img_data[list(img_data.keys())[0]]["imageinfo"][0]["url"]
        except:
            img_url = None
        critters["fish"].append({
            "name": f['title'],
            "img_url": img_url,
            "data": critter_lookup(f['title'], 'fish')
        })
    return critters


def villager_lookup(villager):
    attributes = ["species", "gender", "personality", "birthday", "clothes", "starsign", "phrase"]
    page = requests.get('https://nookipedia.com/wiki/' + villager)
    villager_data = {}
    if page.status_code == 404:
        return None
    else:
        tree = html.fromstring(page.content)

        for att in attributes:
            id = str("Infobox-villager-" + att)
            temp = str(tree.xpath('//td[@id="' + id + '"]//text()'))
            if att in ["species", "gender", "personality", "birthday", "starsign"]:
                temp = temp.replace("['","").replace("']","").replace("*","").replace("', '","")
                temp = temp[:-2]
            if att == "clothes":
                temp = temp[2:-13]
                temp = temp.split("', '*', '")
            if att == "phrase":
                tempp = re.sub('[\'",\\\\n\[\]]', '', temp)
                tempp = tempp.split()
                temp = []
                for w in tempp:
                    if w == 'More':
                        break
                    if w != '*':
                        temp.append(w)
            if temp == '':
                temp = None
            villager_data[att] = temp
    return villager_data


def critter_lookup(name, type):
    page = requests.get('https://nookipedia.com/wiki/' + name)
    if page.status_code == 404:
        return None
    else:
        tree = html.fromstring(page.content)

        temp = str(tree.xpath(f'//table[@id="Infobox-{type}"]//text()'))
        temp = re.sub(r"['\",[\]]", "", temp)
        temp = re.sub(r" {2}", " ", temp)
        temp = temp.split("\\n")
        temp = [i.strip() for i in temp if i and i != ' ']
        temp = temp[5:]
        data = {}
        for i in range(1, len(temp), 2):
            if temp[i-1] == "Main Appearances":
                break
            else:
                data[temp[i-1]] = re.sub(r" {2}", " ", temp[i])
        return data


if __name__ == '__main__':
    # Test Villager Lookup
    # for v in ["Stitches", "Cube", "Apollo", "Apple", "Bob", "Bud", "Octavian"]:
    #     print(f"{v}:\n{villager_lookup(v)}")

    # Get Critters Test!
    # print(critter_lookup("Goldfish", "fish"))
    # print()
    # print(critter_lookup("Goliath Beetle", "bug"))
    # print()
    # print(critter_lookup("bee", "bug"))

    # print(get_critters())

    villager_data = get_villagers()
    with open('villagers.json', 'w', encoding='utf-8') as f:
        json.dump(villager_data, f, ensure_ascii=False, indent=4)

    critter_data = get_critters()
    with open('critters.json', 'w', encoding='utf-8') as f:
        json.dump(critter_data, f, ensure_ascii=False, indent=4)
