#!/usr/bin/env python

import json
import re
import string

from collections import Counter

datafile = "debug20.json"
datafile = "recipeitems-latest.json"

def fetchjson():
    with open(datafile) as f:
        lines = [json.loads(line) for line in f]
        print len(lines), 'recipes read'
        return lines #[:1]


quarter = r'(\xbc)'
half = r'(\xbd)'
three_quarters = r'(\xbe)'

# https://www.debuggex.com/r/NNU9Mgn08HsUVN6U
expr = r'(?:\d+[ -]?)?(?:\d+/\d+|\xbc|\xbd|\xbe)|\d*\.\d+|\d+'

## if we want to get ranges, e.g: 1/2 - 3/4
expr = r'(?:' + expr + r')(?:\s*-\s*(?:' + expr + r'))?'

## if we want to get the quantity as well at once
expr_with_quants = r'(?:'+ expr +')\s+\w+'

## float regexp
r_float = r'\d*\.?\d+'

first_wash_accepted_signs = '-/.:'
unwanted_signs = string.punctuation.translate(None, first_wash_accepted_signs)
translation_table_1 = dict.fromkeys(map(ord, unwanted_signs), None)
translation_table_2 = dict.fromkeys(map(ord, first_wash_accepted_signs), None)

def parse_float(input):
    floats = re.findall(r_float, input)
    if len(floats)>0:
        return float(floats[0])
    return 0.0

def parse_cnt(input):
    range_index = input.find("-")
    if range_index >= 0:
        input = input [:range_index].strip()

    slash_index = input.find("/")
    count = 0.0
    if slash_index >= 0:
        count = count + parse_float(input[:slash_index].strip()) / parse_float (input[slash_index:].strip())
    else:
        count = count + parse_float(input)
    count = count + len(re.findall(quarter, input)) * 0.25
    count = count + len(re.findall(half, input)) * 0.5
    count = count + len(re.findall(three_quarters, input)) * 0.75
    
    return count

def parse_ing_list(ingredients):
    results = []
    for ing in ingredients:
        ing = ing.lower()
        ing = ing.translate(translation_table_1)
        if len(ing) == 0:
            continue
        #skip headers like "sauce:", "topping:", etc.
        if ing[-1] == ":":
            continue
        counts = re.findall(expr, ing)
        if len(counts) == 0:
            results.append((ing.strip(), u'unknown', 1))
            continue
        units_end_index = ing.find(counts[-1]) + len (counts[-1])
        full_name = ing[units_end_index:].strip()
        if len (full_name) == 0:
            continue
        last_quantity = full_name.split()[0]
        name = full_name[len(last_quantity):].strip().translate(translation_table_2)
        if name.startswith('of'):
            name = name.replace('of', '').strip()
        if len(name) == 0:
            continue
        for cnt in counts:
            start_index = ing.find(cnt)
            end_index = start_index + len(cnt)
            ing_tail = ing[end_index:].strip()
            quant = ing_tail.split()[0].strip()
            cnt_float = parse_cnt(cnt)

        	# print '@ile i czego', [cnt, quant, name]
        	## if we want only the last one count-quantity pair, uncomment
        	# if cnt == counts[-1]:
            results.append((name, quant, cnt_float))
        # print counts, [ing.strip()]
    # return list of tuples: [("flour", "cup", 1.5), ("water", "oz", 20.0)]
    return results

def parse_ingredients(ings):
    result = []
    for ing in ings:
        ing_list = [i.strip() for i in ing.split('\n')]
        result.extend(parse_ing_list(ing_list))
    return result

def main():
    lines = fetchjson()
    ings = [line['ingredients'] for line in lines]
    result = parse_ingredients(ings)
    grouped = zip(*result)
    # ings, quants, cnts = grouped
    for group in grouped:
        cnt = Counter(group)
        for what in cnt.most_common(50):
            print what
        print '###'
    # for ing, quant, cnt in result:
    #     # print (ing, quant, cnt)
    #     print quant.encode('utf-8')


if __name__ == '__main__':
    main()

