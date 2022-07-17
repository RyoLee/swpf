import json
from os import system


def getScore(card, comparison):
    score = 0
    for key in card:
        if card[key] == comparison[key]:
            score = score + 1
    return score

def run_gabes_code():
    deck = []
    print("复制并粘贴你的卡组文件(.ydk格式)中#main到下一个#开头部分(为#side或#extra)的全部数字,不包含#main和#side,", 
        "(完成后按2次回车结束): ")
    while True:
        user_input = input()
        if user_input == '':
            break
        elif len(user_input) == 7:
            #appending a 0 to front to work with EDOPRO YDK files
            #that delete leading zeros....
            user_input = '0' + user_input
            deck.append(int(user_input))
        elif len(user_input) != 8:
            pass
        else:
            deck.append(int(user_input))
    # remove duplicates
    deck = set(list(deck))

    deckmonsters = {}
    monsterbridges = {}

    # Step 2: API Calls
    for card in deck:
        for k,v in cards_db.items():
            if card == k:
                deckmonsters[v["names"][0]] = {
                    "atk": v["atk"],
                    "def": v["def"],
                    "attribute": v["attribute"],
                    "type": v["race"],
                    "level": v["level"],
                }

    monster_names = set(deckmonsters.keys())

    # Step 3: Actual Logic


    for card in deckmonsters:
        monsterbridges[card] = []
        for key in deckmonsters:
            score = getScore(deckmonsters[card], deckmonsters[key])
            if score == 1:
                monsterbridges[card].append(key)


    # Right Now, monster-bridges is a dict with all cards that connect to each other. Now, we want to output all the cards each card can search

    missing = {}
    print("---全部可能的检索路径---")
    with open("output.csv", "w") as f:
        f.write(f"手卡,卡组,检索\n")
        for card in monsterbridges:
            targets = set()
            for key in monsterbridges[card]:
                for target in monsterbridges[key]:
                    print(f"除外 {card} ---> 展示 {key} ---> 检索 {target}")
                    f.write(f"{card},{key},{target}\n")
                    targets.add(target)
            missing[card] = monster_names - targets - {card}

    print()
    print("---结果已保存为output.csv文件,请使用Excel/WPS查看搜索---")


def init_data():
    db = {}
    cards = None
    with open("cards.json", "r", encoding="UTF-8") as f:
        cards = json.load(f)
    for v in cards.values():
        card  = {}
        if "data" not in v:
            continue
        if v["data"]["race"] == 0:
            continue
        card["atk"] = v["data"]["atk"]
        card["def"] = v["data"]["def"]
        card["attribute"] = v["data"]["attribute"]
        card["level"] = v["data"]["level"]
        card["race"] = v["data"]["race"]
        card["names"] = []
        if "cn_name" in v:
            card["names"].append(v["cn_name"])
        if "cnocg_n" in v:
            card["names"].append(v["cnocg_n"])
        if "jp_ruby" in v:
            card["names"].append(v["jp_ruby"])
        if "jp_name" in v:
            card["names"].append(v["jp_name"])
        if "en_name" in v:
            card["names"].append(v["en_name"])
        if len(card["names"])== 0:
            print("-------wtf-------")
        if card['atk'] == -2:
            card['atk'] = - v['cid']
        if card['def'] == -2:
            card['def'] = - v['cid']
        db[v['id']]=card
    return db

def given_card_name_get_attrs(cardName):
    attr_dict = {}
    for card in cards_db.values():
        #ignore case
        if cardName in card["names"]:
            attr_dict["atk"] = card["atk"]
            attr_dict["def"] = card["def"]
            attr_dict["attribute"] = card["attribute"]
            attr_dict["level"] = card["level"]
            attr_dict["race"] = card["race"]

    return attr_dict


def exactly_one_equal(card, attrs):
    similar_attrs = 0
    if attrs["atk"] == card["atk"]:
        similar_attrs += 1
    if attrs["def"] == card["def"]:
        similar_attrs += 1
    if attrs["attribute"] == card["attribute"]:
        similar_attrs += 1
    if attrs["level"] == card["level"]:
        similar_attrs += 1
    if attrs["race"] == card["race"]:
        similar_attrs += 1
    return similar_attrs == 1

def find_bridge(name1, name2):
    attrs1 = given_card_name_get_attrs(name1)
    attrs2 = given_card_name_get_attrs(name2)

    card_list = []
    bridge_list = []
    for card in cards_db.values():
        if exactly_one_equal(card, attrs1):
            card_list.append(card)
    for card in card_list:
        if exactly_one_equal(card, attrs2):
            bridge_list.append(card)

    for i in range(len(bridge_list)):
        print(f'{i + 1}. {bridge_list[i]["names"][0]}')

def verify_card_legality(cardName):
    attr_dict = given_card_name_get_attrs(cardName)
    if attr_dict == {}:
        print(
            cardName,
            "不是正确的卡片名.",
        )
        return False
    return True


def find_small_world_compatible(name):
    attrs = given_card_name_get_attrs(name)

    card_list = []
    for card in cards_db.values():
        if exactly_one_equal(card, attrs):
            card_list.append(card)

    for i in range(len(card_list)):
        print(f'{i + 1}. {card_list[i]["names"][0]}')


def main():
    while True:
        mode = input(
"""
从手卡除外 A , 从卡组展示 B , 从卡组检索 C 

选择模式:

1. 路径查找模式
   输入卡片 A 与 C 查找可能的卡片 B.

2. 单卡查找模式
   攻/防/等级/类型/属性仅1个相同的所以卡.

3. YDK卡组路径生成
   通过YDK卡组ID生成卡组检索路径.

q. 退出
选择: """
        )

        if mode == "1":
            card1 = input("手卡卡片名: ").strip()
            card2 = input("检索卡片名: ").strip()
            print('--------------')
            if verify_card_legality(card1) and verify_card_legality(card2):
                find_bridge(card1, card2)
        elif mode == "2":
            card = input(
                "查找关联卡片名: "
            ).strip()
            print('--------------')
            if verify_card_legality(card):
                find_small_world_compatible(card)
        elif mode == "3":
            print('--------------')
            run_gabes_code()

        elif mode == "q":
            break
        else:
            print("请输入 1/2/3/q")


cards_db = init_data()

if __name__ == "__main__":
    main()
system("pause")