CREATE TYPE roaprefix AS(
prefix  cidr,
maxlen  int8
);

CREATE OR REPLACE FUNCTION roaprefix(
    cidr,
    int8
) RETURNS roaprefix AS
$$
SELECT ($1,$2)::roaprefix;
$$
LANGUAGE 'sql' IMMUTABLE STRICT
COST 1;


CREATE OR REPLACE FUNCTION roaprefix_overlaps(inet, roaprefix)
RETURNS boolean AS
$$
SELECT ($1) >>= ($2).prefix OR ($1) <<= ($2).prefix;
$$
LANGUAGE 'sql' IMMUTABLE;

CREATE OR REPLACE FUNCTION roaprefix_overlaps(roaprefix, inet)
RETURNS boolean AS
$$
SELECT ($2) >>= ($1).prefix OR ($2) <<= ($1).prefix;
$$
LANGUAGE 'sql' IMMUTABLE;


CREATE OPERATOR @> (
LEFTARG = roaprefix,
RIGHTARG = inet,
PROCEDURE = roaprefix_overlaps
);


CREATE OPERATOR <@ (
LEFTARG = inet,
RIGHTARG = roaprefix,
PROCEDURE = roaprefix_overlaps
);