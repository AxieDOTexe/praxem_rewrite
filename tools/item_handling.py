import os

from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv('.env')
dbclient = MongoClient(os.getenv('DBSTRING1'))
db = dbclient[os.getenv('DBSTRING2')]


def create_inventory(id, main_weapon, secondary_weapon):
    item_list = inventory_list()[5:]

    dictionary = {"_id": id,"main_weapon": main_weapon,"secondary_weapon": secondary_weapon,
                  "main_weapon_xp": 0,"secondary_weapon_xp": 0,"balance": 0}

    for i in range(len(item_list)):
        dictionary[item_list[i]] = 0

    db["Inventory"].insert_one(dictionary)


def inventory_list():
    li = []
    item = db["Items"].find({"_id": "item_definitions"})
    for i in item:
        li = i["item_list"]

    return li


def get_item_emote(item, bot):
    emote = '❓'

    items = db["Items"].find({"_id": item})
    for i in items:
        emote = bot.get_emoji(i["emote_id"])

    return emote


def decorate_inventory_items(list, bot):
    items_to_pop = []

    for i in range(len(list)):
        li = list[i].split(': ')

        '''# INSERT EMOTE HERE TOO LATER'''
        name = li[0]
        print(name)
        value = li[1]
        emote = get_item_emote(name.replace(" ", "_"), bot)

        li = f"{emote} {name}\n— *Amount: `{value}`*"
        list[i] = li

        '''if value = 0, add to pop list'''
        if int(value) == 0:
            items_to_pop.append(i)

    '''items to remove if value = 0'''
    for i in range(len(items_to_pop)):
        list.pop(items_to_pop[i] - i)

    return list


def decorate_inventory_list(list):
    # main weapon, second weapon, main weapon xp, secondary weapon xp, balance
    for i in range(0, 5):
        list[i] = list[i].split(': ')[1]

    # main and secondary weapon strings
    list[0] = f"*{list[2]} XP* — **{list[0].capitalize()}**"
    list[1] = f"*{list[3]} XP* — **{list[1].capitalize()}**"

    return list
