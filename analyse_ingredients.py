#!/usr/bin/env python

import json
import re

datafile = "debug20.json"
#datafile = "recipeitems-latest.json"

def fetchjson():
    with open(datafile) as f:
        lines = [json.loads(line) for line in f]
        print len(lines), 'recipes read'
        return lines #[:1]


expr = r'(?:\d+[ -]?)?(?:\d+/\d+|\xbc|\xbd|\xbe)|\d*\.\d+|\d+'

## if we want to get ranges, e.g: 1/2 - 3/4
expr = r'(?:' + expr + r')(?:\s*-\s*(?:' + expr + r'))?'

## if we want to get the quantity as well at once
expr_with_quants = r'(?:'+ expr +')\s+\w+'

def parse_ing_list(ingredients):
    results = []
    for ing in ingredients:
        counts = re.findall(expr, ing)
        for cnt in counts:
        	start_index = ing.find(cnt)
        	end_index = start_index + len(cnt)
        	ing_tail = ing[end_index:].strip()
        	quant = ing_tail.split()[0].lower()
        	name = ing_tail[len(quant):].strip().lower()
        	if name.startswith('of'):
        		name = name.replace('of', '').strip()
        	# print '@ile i czego', [cnt, quant, name]
        	## if we want only the last one count-quantity pair, uncomment
        	# if cnt == counts[-1]:
        	results.append((name, quant, cnt))
        if len(counts) == 0:
        	results.append((ing.strip().lower(), 'unknown', 1))
        # print counts, [ing.strip()]
    # return list of tuples: [("flour", "cup", 1.5), ("water", "oz", 20.0)]
    return results


def main():
    lines = fetchjson()
    ings = [line['ingredients'] for line in lines]
    for ing in ings:
        ing_list = [i.strip() for i in ing.split('\n')]
        print parse_ing_list(ing_list)
        for i in ing_list:
            # print [i]
            pass


if __name__ == '__main__':
    main()

