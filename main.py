#!/usr/bin/env python
# -*- coding: utf-8 -*- 


from sqlalchemy import *
import json
import re

datafile = "debug20.json"
#datafile = "recipeitems-latest.json"

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
        return lines #[:1]


def depopulate():
    metadata = MetaData(db)
    for tablename in ['recipes_ingredients', 'recipes', 'ingredients', 'quantities', 'categories']:
        table = Table(tablename, metadata, autoload=True)
        delete = table.delete()
        delete.execute()

def parse_single_time(input):
    unit = input[len(input)-1]
    value = int(re.findall('[0-9]+',input)[0])
    if unit == 'S':
        return value
    elif unit == 'M':
        return value*60
    elif unit == 'H':
        return value*60*60

def parse_time(input):
    seconds = 0
    for time in re.findall('[0-9]+[A-Z]+',input):
        seconds = seconds + parse_single_time(time)
    return seconds

def tables_from_recs(records):
    recipes, ingredients, quantities, categories = [], [], [], []
    ingredients = [rec['ingredients'] for rec in records]
    quantities = ['glass']
    for rec in records:
        try:
            categories.append(rec['recipeCategory'])
        except (KeyError) as e:
            pass
        good_fields = ['name', 'description', 'url', 'image', 'source']
        nrec = {field: rec[field] for field in good_fields if field in rec}
        try:
            nrec['ing_list'] = parse_ing_list(rec['ingredients'])
            if int(rec.get('recipeYield')):
                nrec['recipeyield'] = rec['recipeYield']
        except (TypeError, ValueError) as e:
            pass
        if rec.get('recipeCategory'):
            nrec['category_id'] = rec['recipeCategory']
        if rec.get('datePublished'):
            nrec['date_published'] = rec['datePublished']
        if rec.get('cookTime'):
            nrec['cook_time'] = parse_time(rec['cookTime'])
        if rec.get('prepTime'):
            nrec['prep_time'] = parse_time(rec['prepTime'])
        if rec.get('totalTime'):
            nrec['total_time'] = parse_time(rec['totalTime'])
        recipes.append(nrec)
        # print [nrec]
    return recipes, ingredients, quantities, categories


def run(stmt):
    rs = stmt.execute()
    for row in rs:
        print row


def parse_ing_list(ingredients):
    ing_list = [ing.strip() for ing in ingredients.split('\n')]
    # return list of tuples: [("flour", "cup", 1.5), ("water", "oz", 20.0)]
    return [(ingredients, 'glass', 1.0)]

def get_dict(table):
    table_set = set(table)
    return {i: -1 for i in table_set}

def get_recip_list(recipes, cat_dict):
    for rec in recipes:
        if rec.get('category_id') is not None:
            rec['category_id'] = cat_dict[rec['category_id']]
        rec['dbid'] = -1
    return recipes

def insert_names(name_dict, tablename):
    metadata = MetaData(db)
    table = Table(tablename, metadata, autoload=True)
    insert = table.insert()
    new_name_dict = {}
    for name in name_dict:
        idd = insert.execute({'name':name}).inserted_primary_key
        new_name_dict[name] = idd[0]
    return new_name_dict

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

def populate():
    # -pobierz dane w formacie json z pliku
    records = fetchjson()

    tables = tables_from_recs(records)

    recipes, ingredients, quantities, categories = tables

    # -wyznacz zbiór różnych categories
    cat_dict = get_dict(categories)
    # -insert categories po kolei, z zapisaniem przy nich id wstawionego elementu
    cat_dict = insert_names(cat_dict,"categories")

    # -wyznacz zbiór różnych ingredients
    ingred_dict = get_dict(ingredients)
    # -insert ingredientów po kolei, z zapisaniem przy nich id wstawionego elementu
    ingred_dict = insert_names(ingred_dict,"ingredients")

    # -wyznacz zbiór różnych quantities
    quant_dict = get_dict(quantities)
    # -insert quantities po kolei, z zapisaniem przy nich id wstawionego elementu
    quant_dict = insert_names(quant_dict,"quantities")

    # -wyznacz zbiór różnych przepisów
    recip_list = get_recip_list(recipes, cat_dict)
    # -insert przepisow po kolei, z zapisaniem przy nich id wstawionego
    recip_list = insert_recips(recip_list)
    
    # -dla każdego przepisu, przejechanie po ingredientach i quantities i zastapienie ich przez odpowiednie id
    recip_ingreds = get_recip_ingreds(ingred_dict, quant_dict, recip_list)
    # -insert takich struktur do recip_ingred
    # print recip_ingreds
    insert_recip_ingreds(recip_ingreds)
    print len(recip_ingreds), 'recip_ingreds inserted'


if __name__ == '__main__':
    print "depopulating"
    depopulate()
    print "populating"
    populate()

