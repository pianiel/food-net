#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import json
import re
import string
import copy

from collections import Counter

datafile = "recipeitems-latest.json"
#datafile = "debug20.json"
#datafile = "debug300.json"

def fetchjson():
    with open(datafile) as f:
        lines = [json.loads(line) for line in f]#.decode('ascii', 'ignore')
        print len(lines), 'recipes read'
        #return random.sample(lines,100) #AWESOME for debug purposes
        return lines #[:1]


quarter = r'(\xbc)'
half = r'(\xbd)'
three_quarters = r'(\xbe)'

# https://www.debuggex.com/r/NNU9Mgn08HsUVN6U
expr = r'(?:\d+[ ]?)?(?:\d+/\d+|\xbc|\xbd|\xbe)|\d*\.\d+|\d+'

## if we want to get ranges, e.g: 1/2 - 3/4
expr = r'(?:' + expr + r')(?:\s*-\s*(?:' + expr + r'))?'

## if we want to get the quantity as well at once
expr_with_quants = r'(?:'+ expr +')\s+\w+'

## float regexp
r_float = r'\d*\.?\d+'
##int regexp, to take care of i.e. '2.'
r_int = r'\d+' 

first_wash_accepted_signs = '-/.:'
unwanted_signs = string.punctuation.translate(None, first_wash_accepted_signs)
translation_table_1 = dict.fromkeys(map(ord, unwanted_signs), None)
translation_table_2 = dict.fromkeys(map(ord, first_wash_accepted_signs), None)

def parse_float(input):
    floats = re.findall(r_float, input)
    if len(floats)>0:
        return float(floats[0])
    ints = re.findall(r_int, input)
    if len(ints)>0:
        return int(ints[0])
    return 0.0

def parse_cnt(input):
    range_index = input.find("-")
    if range_index >= 0:
        input = input [:range_index].strip()
    
    space_index = input.find(" ")
    count = 0.0
    if space_index >= 0:
        count = count + parse_float(input[:space_index].strip())
        input = input[space_index:].strip()
    slash_index = input.find("/")
    if slash_index >= 0:
        count = count + parse_float(input[:slash_index].strip()) / parse_float (input[slash_index:].strip())
    else:
        count = count + parse_float(input)
    count = count + len(re.findall(quarter, input)) * 0.25
    count = count + len(re.findall(half, input)) * 0.5
    count = count + len(re.findall(three_quarters, input)) * 0.75
    return count

def unify_units(unit):
    if unit in ['tsp', 'tsps', 'teaspoon', 'teaspoons', 'ts', 'sp', 'spoon']:
        unit = u'teaspoon'
    elif unit in ['tbsp', 'tbsps', 'tablespoon', 'tablespoons', 'tb', 'tbs']:
        unit = u'tablespoon'
    elif unit in ['oz', 'ozs', 'ounce', 'ounces']:
        unit = u'oz'
    elif unit in ['g', 'gs', 'gram', 'grams']:
        unit = u'g'
    elif unit in ['kg', 'kgs', 'kilogram', 'kilograms', 'kgrams', 'kgram']:
        unit = u'kg'
    #maybe unify plural forms later, for all units?
    elif unit in ['dash', 'dashes']:
        unit = u'dash'
    elif unit in ['cup', 'cups']:
        unit = u'cup'
    elif unit in ['lb', 'lbs', 'lbm', 'pound', 'pounds']:
        unit = u'pound'
    return unit

stoplist = ['of', 'and', 'or', 'zo', 'c', 'in', 'f', 'to', 'as', 'to', 'one', 'beaten', 'weight', 'oz', 'white', 'dry', 'raw', 'hot', 'old', 'fresh', 'jar', 'de', 'so', 'all', 'me', 'can', 'round', 'fine', 'extra','pie','sauce','pack','powder','cut','fluid','thin','gin','pot','rum','ounces','for','tin','if','mix','cube','fat','into','the','ice','up','cans','quart','quarts','finely','stock','cubes', 'cream', 'ground','piece','pieces','baking','juice','seeds','leaf','leaves','nut','nuts','thick','more','peas','bag','thinly','green','pan', 'taste', 'skin', 'each', 'cup', 'pinches', 'half', 'with', 'paste', 'slice','cold', 'spice','frozen', 'whole','chile', 'plus', 'dice', 'top', 'chunks', 'syrup', 'bar','package', 'small','stick', 'bone', 'fish', 'not','shortening', 'use','crust', 'size', 'off', 'seasoning', 'free', 'lb', 'from', 'ale','amp','plain', 'pod','strips', 'total', 'large', 'wedge', 'leg', 'ripe','lightly', 'dish','optional', 'fruit', 'fruits','stem', 'jam', 'peel', 'port', 'stalk', 'shell', 'flower', 'torn', 'tub', 'fillet', 'breast', 'meat','roughly','garni','salsa', 'length', 'serve', 'head','long', 'only','room temperature','well','rounds', 'brown', 'bunch', 'meal', 'squash', 'beet', 'yellow', 'coarsely', 'ones', 'dates', 'box', 'heart', u'\u215e ounces weight','loaf', 'rings', 'less', 'liquid', 'ready', 'container', 'blend', 'then','cod','over', 'lean', 'sheet', 'solids', 'hard', 'square', 'spoon', 'ends', 'bottle', 'wide', 'halves', 'bits','diameter','recipe','ball','extract', 'thighs','packet','on', 'but', 'pin','see', 'soy', 'out', 'cake', 'vegetable', 'edges','fillets', 'sticks', 'halfandhalf', 'grain', 'stems', 'rib', 'cups', 'at room temperature','hearts','broken','bulb','such as','split','dressing','rind','breasts', 'medium','lengths','lengthwise','jars','pit','greens','freshly','liver', 'chops','smoke', 'squares', 'oven', 'flakes', 'neck', 'balls', 'wings', 'sheets', 'thickly', 'serving', 'pns', 'legs', 'heads', 'tops', 'tails', 'tins', 'deep', 'dog', 'tips', 'crusts', 'a jar', 'bars', 'thickness', 'be','slices','heat','you','soup','light','bun','parts','note','tip','jus','bones','loin','roast','cob','lengthways','mince','bags','pound','block','clean','preferably','until','coating','tsp','bes','pea','soft','left','like','prefer','below','palm','base','slightly','cn','\u2013','bulbs','triple sec','core','about','rest','segments','skins','using','organic','filling','pans','bitesize','cooking','loosely','person','excess','fat','spread','spoons','both','bake','colour','sole','dogs','fingers','very','twist','flowers','sides','when','intact','fork','is','fine','decorate','content','range','good','spicy','portion','above','snow','at','left','bottles']


def startswith (name, stoplist):
    for string in stoplist:
        if name.startswith(string+' ') or name == string :
            return True
    return False

def parse_ing_list(current_results, ingredients):
    results = []
    for ing in ingredients:
        ing = ing.lower()
        ing = ing.translate(translation_table_1).strip()
        #remove all words ending with 'ed' (practically only adjectives)
        ing = re.sub(r'\w+ed(\s|$)','',ing)
        if len(ing) == 0:
            continue
        #skip headers like "sauce:", "topping:", etc.
        if ing[-1] == ":":
            continue
        counts = re.findall(expr, ing)
        if len(counts) == 0:
            #very dirty data
            #results.append((ing.strip(), u'unknown', 1))
            continue
        units_end_index = ing.rfind(counts[-1]) + len (counts[-1])
        full_name = ing[units_end_index:].translate(translation_table_2).strip()
        if len (full_name) == 0:
            continue
        last_quantity = full_name.split()[0]
        name = full_name[len(last_quantity):].strip()
        while startswith(name, stoplist):
            for word in stoplist:
                if name.startswith(word+' ') or name == word:
                    name = name.replace(word, '').strip()
        if len(name) == 0:
            continue
        #print ing
        for cnt in counts:
            start_index = ing.find(cnt)
            end_index = start_index + len(cnt)
            ing = ing[end_index:].strip()
            quant = ing.translate(translation_table_2).strip().split()[0]
            #for s in first_wash_accepted_signs:
            #    quant = quant.split(s)[0]
            cnt_float = parse_cnt(cnt)

        	## if we want only the last one count-quantity pair, uncomment
        	# if cnt == counts[-1]:
            if 0.0 == parse_cnt(quant): #add only if quantity is not a number (happens with two following numbers i.e. 2 3 ounce oranges)
                #print cnt_float, quant, name
                results.append((name, unify_units(quant), cnt_float))
        # print counts, [ing.strip()]
    # return list of tuples: [("flour", "cup", 1.5), ("water", "oz", 20.0)]
    return results

def parse_ingredients(ings):
    result = []
    for ing in ings:
        ing_list = [i.strip() for i in ing.split('\n')]
        result.extend(parse_ing_list(result, ing_list))
    return result

def main():
    lines = fetchjson()
    ings = [line['ingredients'] for line in lines]
    result = parse_ingredients(ings)
    grouped = zip(*result)
    # ings, quants, cnts = grouped
    print 'Total of', len(grouped[0]), 'ingredients found,'

    unique_ingredients = set(grouped[0])
    cntr = Counter(grouped[0])
    print len(unique_ingredients), 'unique ones'
    #This will take a loooot of time [ O((100 000)^2) ]
    mappings = {}
    for what in cntr.most_common(len(unique_ingredients)/10): # we need a constant here because otherwise we get rubbish ingredient as the most popular one...
        n1 = what [0]
        for n2 in unique_ingredients:
            if n1 in n2 and n2 != n1: #only one mapping per ingredient, but what can we do? :<
                if n2 not in mappings or (n2 in mappings and len(n1) < len (mappings[n2])):
                    mappings [n2] = n1
    print 'Found', len(mappings), 'mappings'

    new_result = []
    for ing in result:
        if ing[0] in mappings:
            #print 'Adding', mappings[ing[0]], 'instead of', ing[0]
            new_result.append((mappings[ing[0]], ing[1], ing[2]))
        else:
            new_result.append((ing[0], ing[1], ing[2]))
    grouped = zip(*new_result)

    #for group in grouped:
    group = grouped[0]
    print len(set(group)), 'unique values'
    cnt = Counter(group)
    for what in cnt.most_common(500):
        print what
    print '###'

if __name__ == '__main__':
    main()

