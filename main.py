#!/usr/bin/env python
# -*- coding: utf-8 -*- 


from sqlalchemy import *
import json


datafile = "debug20.json"

user = 'postgres'
password = 'recipes'
host = 'localhost'
dbname = 'food'
dbstring = 'postgresql://' + user + ':' + password + '@' + host + '/' + dbname

db = create_engine(dbstring)

def fetchjson():
    with open(datafile) as f:
        lines = [json.loads(line) for line in f]
        print len(lines), 'recipes read'
        return lines


def depopulate():
    metadata = MetaData(db)
    for tablename in ['recipes_ingredients', 'recipes', 'ingredients', 'quantities']:
        table = Table(tablename, metadata, autoload=True)
        delete = table.delete()
        delete.execute()


def tables_from_recs(records):
    recipes, ingredients, quantities = [], [], []
    ingredients = [rec['ingredients'] for rec in records]
    quantities = ['glass']
    for rec in records:
        good_fields = ['name', 'description', 'url', 'image', 'source']
        nrec = {field: rec[field] for field in good_fields}
        try:
            nrec['ing_list'] = parse_ing_list(rec['ingredients'])
            if int(rec.get('recipeYield')):
                nrec['recipeyield'] = rec['recipeYield']
        except (TypeError, ValueError) as e:
            pass
        # TODO add date and times
        # print [nrec]
        recipes.append(nrec)
    return recipes, ingredients, quantities


def run(stmt):
    rs = stmt.execute()
    for row in rs:
        print row

def parse_ing_list(ingredients):
    # return list of tuples: [("flour", "cup", 1.5), ("water", "oz", 20.0)]
    return [(ingredients, 'glass', 1.0)]


def get_ingred_dict(ingredients):
    ing_set = set()
    for ing_list in ingredients:
        # for ing in ing_list:
        ing_set.add(ing_list)
    return {i: -1 for i in ing_set}

def get_quant_dict(quantities):
    quant_set = set()
    for quant_list in quantities:
        # for quant in quant_list:
        quant_set.add(quant_list)
    return {q: -1 for q in quant_set}

def get_recip_list(recipes):
    for rec in recipes:
        rec['dbid'] = -1
    return recipes


def insert_ingreds(ingred_dict):
    metadata = MetaData(db)
    ingred_table = Table('ingredients', metadata, autoload=True)
    insert = ingred_table.insert()
    new_ingred_dict = {}
    for ingred in ingred_dict:
        idd = insert.execute({'name':ingred}).inserted_primary_key
        new_ingred_dict[ingred] = idd[0]
    return new_ingred_dict


def insert_quants(quant_dict):
    metadata = MetaData(db)
    quant_table = Table("quantities", metadata, autoload=True)
    insert = quant_table.insert()
    new_quant_dict = {}
    for quant in quant_dict:
        idd = insert.execute({'name': quant}).inserted_primary_key
        new_quant_dict[quant] = idd[0]
    return new_quant_dict


def insert_recips(recip_list):
    metadata = MetaData(db)
    recip_table = Table("recipes", metadata, autoload=True)
    insert = recip_table.insert()
    for recip in recip_list:
        idd = insert.execute(recip).inserted_primary_key
        recip['dbid'] = idd[0]
    return recip_list

def get_recip_ingreds(ingred_dict, quant_dict, recip_list):
    recip_ingreds = []
    for recip in recip_list:
        if recip.get('ing_list') is not None:
            for ing_tuple in recip['ing_list']:
                ing, quant, cnt = ing_tuple
                ri_dict  = {}
                ri_dict['ingredient_id'] = ingred_dict[ing]
                ri_dict['quantity_id'] = quant_dict[quant]
                ri_dict['recipe_id'] = recip['dbid']
                ri_dict['quantity_count'] = cnt
                recip_ingreds.append(ri_dict)
    return recip_ingreds

def insert_recip_ingreds(recip_ingred_list):
    metadata = MetaData(db)
    recip_ingred_table = Table("recipes_ingredients", metadata, autoload=True)
    insert = recip_ingred_table.insert()
    for recip_ingred in recip_ingred_list:
        insert.execute(recip_ingred)

def do_work():
    # -pobierz dane w formacie json z pliku
    records = fetchjson()

    tables = tables_from_recs(records)
    recipes, ingredients, quantities = tables

    # -wyznacz zbiór różnych ingredients
    ingred_dict = get_ingred_dict(ingredients)
    # -wyznacz zbiór różnych quantities
    quant_dict = get_quant_dict(quantities)
    # -wyznacz zbiór różnych przepisów
    recip_list = get_recip_list(recipes)

    # -insert ingredientów po kolei, z zapisaniem przy nich id wstawionego elementu
    ingred_dict = insert_ingreds(ingred_dict)
    # -insert quantities po kolei, z zapisaniem przy nich id wstawionego elementu
    quant_dict = insert_quants(quant_dict)
    # -insert przepisow po kolei, z zapisaniem przy nich id wstawionego
    recip_list = insert_recips(recip_list)

    # -dla każdego przepisu, przejechanie po ingredientach i quantities i zastapienie ich przez odpowiednie id
    recip_ingreds = get_recip_ingreds(ingred_dict, quant_dict, recip_list)
    # -insert takich struktur do recip_ingred
    # print recip_ingreds
    insert_recip_ingreds(recip_ingreds)
    print len(recip_ingreds), 'recip_ingreds inserted'


if __name__ == '__main__':
    # records = fetchjson()
    # populate(records)
    print "hello"
    depopulate()
    do_work()

