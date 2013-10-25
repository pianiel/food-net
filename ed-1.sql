DROP TABLE IF EXISTS recipes_ingredients;
DROP TABLE IF EXISTS recipes;
DROP TABLE IF EXISTS ingredients;
DROP TABLE IF EXISTS quantities;
DROP TABLE IF EXISTS categories;

CREATE TABLE ingredients (
    id bigserial primary key,
    name text
);

CREATE TABLE quantities (
    id bigserial primary key,
    name text
);

CREATE TABLE categories (
    id bigserial primary key,
    name text
);

CREATE TABLE recipes (
    id bigserial primary key,
    category_id bigint references categories,
    name text,
    description text,
    url text,
    image text,
    source text,
    date_published DATE,
    recipeyield int,
    total_time int,
    prep_time int,
    cook_time int
);

CREATE TABLE recipes_ingredients (
    id bigserial primary key,
    recipe_id bigint NOT NULL references recipes,
    ingredient_id bigint NOT NULL references ingredients,
    quantity_id bigint NOT NULL references quantities,
    quantity_count float
);

-- insert into recipes (name, description, url, image, source, date_published, recipeyield, total_time, cook_time, prep_time) values ('glass of water', 'just glass of water', 'www.water.com','www.water.com','www.water.com','2010-10-10',1,1,0,1);
-- insert into ingredients (name) values ('water');
-- insert into quantities (name) values ('glass');
-- insert into recipes_ingredients (recipe_id, ingredient_id, quantity_id, quantity_count) values (1, 1, 1, 1.0);

