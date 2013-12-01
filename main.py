#!/usr/bin/env python
# -*- coding: utf-8 -*- 


from sqlalchemy import *
import json
import re
from analyse_ingredients import *

# datafile = "debug20.json"
datafile = "debug300.json"
# datafile = "recipeitems-latest.json"

user = 'postgres'
password = 'recipes'
host = 'localhost'
dbname = 'food'
dbstring = 'postgresql://' + user + ':' + password + '@' + host + '/' + dbname

mappings = load_obj_from_file(MAPPINGS_FILENAME)

db = create_engine(dbstring, execution_options={'autocommit':'false'})

conn = db.connect()

def fetchjson():
    with open(datafile) as f:
        lines = [json.loads(line) for line in f]
        print len(lines), 'recipes read'
        return lines #[:1]


def depopulate():
    metadata = MetaData(db)
    for tablename in ['recipes_ingredients', 'recipes', 'ingredients', 'quantities', 'categories']:
        try:
            trans = conn.begin()
            table = Table(tablename, metadata, autoload=True)
            # delete = table.delete()
            # delete.execute()
            conn.execute(table.delete())
            trans.commit()
        except:
            trans.rollback()
            raise

def parse_single_time(input):
    unit = input[len(input)-1]
    value = int(re.findall('[0-9]+',input)[0])
    if unit == 'S':
        return value
    elif unit == 'M':
        return value*60
    elif unit == 'H':
        return value*60*60
    return 0

def parse_time(input):
    seconds = 0
    for time in re.findall('[0-9]+[A-Z]+',input):
        seconds = seconds + parse_single_time(time)
    return seconds

def tables_from_recs(records):
    recipes, ingredients, quantities, categories = [], [], [], []
    ingredients = []
    quantities = []
    for rec in records:
        try:
            categories.append(rec['recipeCategory'])
        except (KeyError) as e:
            pass
        good_fields = ['name', 'description', 'url', 'image', 'source']
        nrec = {field: rec[field] for field in good_fields if field in rec}
        try:
            ings_quants_counts= parse_ing_list(rec['ingredients'])
            for entry in ings_quants_counts:
                ingredients.append(entry[0])
                quantities.append(entry[1])
            nrec['ing_list'] = ings_quants_counts
            if int(rec.get('recipeYield')):
                nrec['recipeyield'] = rec['recipeYield']
        except (TypeError, ValueError) as e:
            pass
        if rec.get('recipeCategory'):
            nrec['category_id'] = rec['recipeCategory']
        if rec.get('datePublished'):
            dates = re.findall('\d\d\d\d-\d\d-\d\d', rec['datePublished'])
            if len (dates) > 0:
                nrec['date_published'] = dates[0]
        if rec.get('cookTime'):
            nrec['cook_time'] = parse_time(rec['cookTime'])
        if rec.get('prepTime'):
            nrec['prep_time'] = parse_time(rec['prepTime'])
        if rec.get('totalTime'):
            nrec['total_time'] = parse_time(rec['totalTime'])
        #print nrec
        recipes.append(nrec)
        # print [nrec]
    return recipes, ingredients, quantities, categories


def run(stmt):
    rs = stmt.execute()
    for row in rs:
        print row


def parse_ing_list(ingredients):
    result = parse_ingredients([ingredients])
    if mappings is None:
        return result
    mapped_result = []
    for ing in result:
        if ing[0] in mappings:
            #print 'Adding', mappings[ing[0]], 'instead of', ing[0]
            mapped_result.append((mappings[ing[0]], ing[1], ing[2]))
        else:
            mapped_result.append((ing[0], ing[1], ing[2]))
    # print '###'
    # print 'result:', result
    # print 'mapped_result:', mapped_result
    return mapped_result
    #ing_list = [ing.strip() for ing in ingredients.split('\n')]
    # return list of tuples: [("flour", "cup", 1.5), ("water", "oz", 20.0)]
    #return [(ingredients, 'glass', 1.0)]

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
    new_name_dict = {}
    trans = conn.begin()
    try:
        table = Table(tablename, metadata, autoload=True)
        insert = table.insert()
        for name in name_dict:
            # idd = insert.execute({'name':name}).inserted_primary_key
            idd = conn.execute(insert, {'name':name}).inserted_primary_key
            new_name_dict[name] = idd[0]
        trans.commit()
    except:
        trans.rollback()
        raise
    return new_name_dict

def insert_recips(recip_list):
    metadata = MetaData(db)
    trans = conn.begin()
    try:
        recip_table = Table("recipes", metadata, autoload=True)
        insert = recip_table.insert()
        for recip in recip_list:
            # idd = insert.execute(recip).inserted_primary_key
            idd = conn.execute(insert, recip).inserted_primary_key
            recip['dbid'] = idd[0]
        trans.commit()
    except:
        trans.rollback()
        raise
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
    trans = conn.begin()
    try:
        recip_ingred_table = Table("recipes_ingredients", metadata, autoload=True)
        insert = recip_ingred_table.insert()
        for recip_ingred in recip_ingred_list:
            conn.execute(insert, recip_ingred)
        trans.commit()
    except:
        trans.rollback()
        raise

def populate():
    # -pobierz dane w formacie json z pliku
    print "reading data from json file..."
    records = fetchjson()

    print "parsing recipes..."
    tables = tables_from_recs(records)

    recipes, ingredients, quantities, categories = tables

    print "inserting categories..."
    # -wyznacz zbiór różnych categories
    cat_dict = get_dict(categories)
    # -insert categories po kolei, z zapisaniem przy nich id wstawionego elementu
    cat_dict = insert_names(cat_dict,"categories")

    print "inserting ingredients..."
    # -wyznacz zbiór różnych ingredients
    ingred_dict = get_dict(ingredients)
    # -insert ingredientów po kolei, z zapisaniem przy nich id wstawionego elementu
    ingred_dict = insert_names(ingred_dict,"ingredients")

    print "inserting quantities..."
    # -wyznacz zbiór różnych quantities
    quant_dict = get_dict(quantities)
    # -insert quantities po kolei, z zapisaniem przy nich id wstawionego elementu
    quant_dict = insert_names(quant_dict,"quantities")

    print "inserting recipes..."
    # -wyznacz zbiór różnych przepisów
    recip_list = get_recip_list(recipes, cat_dict)
    # -insert przepisow po kolei, z zapisaniem przy nich id wstawionego
    recip_list = insert_recips(recip_list)
    
    print "inserting recipes_ingredients..."
    # -dla każdego przepisu, przejechanie po ingredientach i quantities i zastapienie ich przez odpowiednie id
    recip_ingreds = get_recip_ingreds(ingred_dict, quant_dict, recip_list)
    # -insert takich struktur do recip_ingred
    # print recip_ingreds
    insert_recip_ingreds(recip_ingreds)
    print len(recip_ingreds), 'recip_ingreds inserted'


if __name__ == '__main__':
    print "depopulating..."
    depopulate()
    print "populating..."
    populate()
    # conn.close()

