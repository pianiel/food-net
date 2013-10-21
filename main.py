#!/usr/bin/env python

from sqlalchemy import *
import json


datafile = "debug20.json"

user = 'postgres'
password = 'recipes'
host = 'localhost'
dbname = 'food'
dbstring = 'postgresql://' + user + ':' + password + '@' + host + '/' + dbname


def fetchjson():
    with open(datafile) as f:
        lines = [json.loads(line) for line in f]
        print len(lines), 'records read'
        return lines


def populate(records):
    print len(records), 'records to populate'
    tables = tables_from_recs(records)
    recipes, ingredients, quantities, rec_ingr = tables
    # print ingredients
    db = create_engine(dbstring)
    metadata = MetaData(db)
    recip_table = Table("recipes", metadata, autoload=True)
    insert = recip_table.insert()
    for recip in recipes:
        insert.execute(recip)
    # run(recipes.select())
    ingred_table = Table('ingredients', metadata, autoload=True)
    insert = ingred_table.insert()
    for ingred in ingredients:
        insert.execute({'name':ingred})


good_fields = ['name', 'description', 'url', 'image', 'source']

def tables_from_recs(records):
    recipes, ingredients, quantities, rec_ingr = [], [], [], []
    ingredients = [rec['ingredients'] for rec in records]
    for rec in records:
        nrec = {field: rec[field] for field in good_fields}
        try:
            int(rec.get('recipeYield'))
            nrec['recipeyield'] = rec['recipeYield']
        except (TypeError, ValueError) as e:
            pass
        # TODO add date and times
        # print [nrec]
        recipes.append(nrec)
    return recipes, ingredients, quantities, rec_ingr


def run(stmt):
    rs = stmt.execute()
    for row in rs:
        print row


if __name__ == '__main__':
    records = fetchjson()
    populate(records)
