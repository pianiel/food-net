-- nodes query 
select id, name as label from ingredients;

--nodes appearing in more than 3 recipes
select s.id, name as label, count from 
(select ingredient_id as id, count(ingredient_id) as count from recipes_ingredients group by ingredient_id) as s 
join ingredients on s.id = ingredients.id where count > 3;

-- edges query
select distinct 
a.ingredient_id as source, 
b.ingredient_id as target, 
count(a.ingredient_id) as weight
from recipes_ingredients as a
join recipes_ingredients as b 
using (recipe_id)
where a.ingredient_id < b.ingredient_id
group by source, target
order by weight desc, source, target;

-- edges query limited to weight > 2
select source, target, weight from
(
select distinct 
a.ingredient_id as source, 
b.ingredient_id as target, 
count(a.ingredient_id) as weight
from recipes_ingredients as a
join recipes_ingredients as b 
using (recipe_id)
where a.ingredient_id < b.ingredient_id
group by source, target
) as s
where s.weight > 2
order by weight desc, source, target;

-- edges query with ingredients names
select i.name, i2.name, weight, source, target from
(
select distinct 
a.ingredient_id as source, 
b.ingredient_id as target, 
count(a.ingredient_id) as weight
from recipes_ingredients as a
join recipes_ingredients as b 
using (recipe_id)
where a.ingredient_id < b.ingredient_id
group by source, target
) as s
join ingredients as i 
on (source = i.id)
join ingredients as i2
on (target = i2.id)
where s.weight > 2
order by weight desc, source, target;
