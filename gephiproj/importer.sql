-- nodes query 
select id, name as label from ingredients;

--nodes appearing in more than 10 recipes
select s.id, name as label, count from 
(select ingredient_id as id, count(ingredient_id) as count from recipes_ingredients group by ingredient_id) as s 
join ingredients on s.id = ingredients.id where count > 10;

--edges using only vertices from the above query
select source, target, weight from 
( select distinct  a.ingredient_id as source,  b.ingredient_id as target,  count(a.ingredient_id) as weight
from recipes_ingredients as a join recipes_ingredients as b  using (recipe_id) 
where a.ingredient_id < b.ingredient_id 
and a.ingredient_id in 
(select s.id from (select ingredient_id as id, count(ingredient_id) as count from recipes_ingredients group by ingredient_id) as s join ingredients on s.id = ingredients.id where count > 10) 
and b.ingredient_id in 
(select s.id from (select ingredient_id as id, count(ingredient_id) as count from recipes_ingredients group by ingredient_id) as s join ingredients on s.id = ingredients.id where count > 10) 
group by source, target ) as s where s.weight > 20 order by weight desc, source, target;

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



-- nodes query so there are no single nodes
with edges as
  (select source, target, weight from 
  ( select distinct  a.ingredient_id as source,  b.ingredient_id as target,  count(a.ingredient_id) as weight
  from recipes_ingredients as a join recipes_ingredients as b  using (recipe_id) 
  where a.ingredient_id < b.ingredient_id 
  and a.ingredient_id in 
  (select s.id from (select ingredient_id as id, count(ingredient_id) as count from recipes_ingredients group by ingredient_id) as s join ingredients on s.id = ingredients.id where count > 10) 
  and b.ingredient_id in 
  (select s.id from (select ingredient_id as id, count(ingredient_id) as count from recipes_ingredients group by ingredient_id) as s join ingredients on s.id = ingredients.id where count > 10) 
  group by source, target ) as s where s.weight > 20 order by weight desc, source, target)

select 
  s.id, 
  name as label, 
  count as size 
  --ln(count) as size --it's better to change the size manually
  from 
  (select ingredient_id as id, count(ingredient_id) as count 
  from recipes_ingredients group by ingredient_id) 
  as s 
join ingredients on s.id = ingredients.id 
where count > 10
and 
(
s.id in (select source as id from edges)
or
s.id in (select target as id from edges)
)