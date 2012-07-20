-- Drop existing database/user
DROP DATABASE IF EXISTS inguandes;
DROP ROLE IF EXISTS inguandes;

CREATE ROLE inguandes LOGIN
  PASSWORD 'icc.123'
  NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE;

-- On Mac OS X, apparently the collation to use is es_ES.UTF-8 (note the dash)
-- On Windows, apparently the collation to use is Spanish_Spain.1252
CREATE DATABASE inguandes
  WITH OWNER = inguandes
       ENCODING = 'UTF8'
       TEMPLATE = template0
       LC_COLLATE = 'es_ES.UTF8'
       LC_CTYPE = 'es_ES.UTF8'
       CONNECTION LIMIT = -1;

