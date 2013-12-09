--nodes query
select id, name from recipes;

--edges query

select 
  ri1.recipe_id as source, 
  ri2.recipe_id as target,
  --ri1.ingredient_id as ing --, 
  count(ri1.ingredient_id) as weight --,
  --ri1.id as id1, 
  --ri2.id as id2
from recipes_ingredients as ri1
join recipes_ingredients as ri2 using (ingredient_id)
where 
ri1.id < ri2.id 
--and ri2.id < 100
group by source, target
order by source, target


-- takie sobie eksperymenty:
-- all recipes_ingredients pairs
select ri.recipe_id, ri.ingredient_id
--, count(ri.ingredient_id) as cnt
from recipes_ingredients as ri
--group by ri.recipe_id
order by ri.recipe_id, ri.ingredient_id
-- result 662902 rows

-- to samo co wyzej ale select distinct
-- result 606841 rows

-- liczba skladnikow na przepis
-- przepisy z conajmniej dwoma skladnikami
select * from (
	select --distinct
 		ri.recipe_id--, ri.ingredient_id
		, count(ri.ingredient_id) as cnt
	from recipes_ingredients as ri
	group by ri.recipe_id
	order by ri.recipe_id--, ri.ingredient_id
	) as s
where s.cnt > 1
-- result 93262 rows


-- przepisy ktore nie maja ani jednego skladnika w tabeli recipes_ingredients
select *
from recipes as r
left join recipes_ingredients as ri
on r.id = ri.recipe_id
where ri.recipe_id is null
order by r.id
--result 54355 rows


-- skladniki ktore wystepuja tylko w jednym przepisie w bazie
select * from (
	select ri.ingredient_id as riid
	--, ri.recipe_id
	, count(ri.recipe_id) as in_recipes
	from recipes_ingredients as ri
	group by ri.ingredient_id
	order by ri.ingredient_id
	--, ri.recipe_id
) as s
join ingredients as i
on i.id = s.riid
where s.in_recipes = 1
--result 3200 rows !!!


-- skladniki ktore wystepuja co najmiej raz w recipes_ingredients
select ri.ingredient_id
--, ri.recipe_id
, count(ri.recipe_id) as in_recipes
from recipes_ingredients as ri
group by ri.ingredient_id
order by ri.ingredient_id
--, ri.recipe_id
-- result 4908 rows

-- czyli wiecej niz raz -> 4908 - 3200 = 1708

n - ilosc skladnikow
k - ile razy wystepuja w recipes_ingredients

k n
1 4908
2 300
3 133
4 114
5 99
6 73
7 50
8 63
9 36
10 28
>10 812

ponizej 4 to jest raczej bulszit i bledy w nazwach

wzialbym skladniki ktore wystepuja tylko w powyzej 10 przepisach