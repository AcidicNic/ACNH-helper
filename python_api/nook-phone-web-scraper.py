from flask import Flask, jsonify, request
from lxml import html
import requests
import re

app = Flask(__name__)


@app.route('/getAll', methods=['GET'])
def get_all():
    data = get_villagers()
    return jsonify({'villagers': data})


@app.route('/getVillagerData/<str:name>', methods=['GET'])
def get_villager_data(name):
    return jsonify({'data': villager_lookup(name)})


def get_villagers():
    url = "https://nookipedia.com/w/api.php?action=query&list=categorymembers&cmtitle=Category:New_Horizons_characters&cmlimit=max&format=json"
    raw_villagers = requests.get(url).json()["query"]["categorymembers"]
    villagers = []
    for v in raw_villagers:
        img = requests.get(f"https://nookipedia.com/w/api.php?action=query&list=allimages&aifrom={v['title']}_NLa.png&aiprop=url&format=json&aisort=name&ailimit=1").json()["query"]["allimages"][0]["url"]
        villagers.append({
            "name": v['title'],
            "img_url": img,
            # "data": villager_lookup(v['title'])
        })
    return villagers


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


if __name__ == '__main__':
    # Test Villager Lookup
    for v in ["Stitches", "Cube", "Apollo", "Apple", "Bob", "Bud", "Octavian"]:
        print(f"{v}:\n{villager_lookup(v)}")