-- nodes query 
select id, name as label from ingredients;

-- edges query
select distinct a.ingredient_id as source, b.ingredient_id as target 
from recipes_ingredients as a
join recipes_ingredients as b 
using (recipe_id)
where a.ingredient_id < b.ingredient_id
order by source, target
group by source, target;