DROP SEQUENCE vdv_seq;
create SEQUENCE vdv_seq start with 1 increment by 1;

DROP TYPE IF EXISTS vdv_prop_type CASCADE;
CREATE TYPE vdv_prop_type AS ENUM ('bool', 'int', 'real', 'media', 'comment', 'like');

DROP TYPE IF EXISTS vdv_media_type CASCADE;
CREATE TYPE vdv_media_type AS ENUM ('image');

DROP TABLE IF EXISTS "vdv_court";
CREATE TABLE "vdv_court" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"name" VARCHAR(256) NOT NULL UNIQUE,
	"desc" VARCHAR(4000) NOT NULL DEFAULT '',
	"location" BIGINT NOT NULL,
	"private" BOOLEAN NOT NULL DEFAULT 'false',
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_user";
CREATE TABLE "vdv_user" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY,
	"username" VARCHAR(256) NOT NULL UNIQUE,
	"e-mail" VARCHAR(256) NOT NULL UNIQUE,
	"status" VARCHAR(256) NOT NULL,
	"private" BOOLEAN NOT NULL DEFAULT 'false',
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_media";
CREATE TABLE "vdv_media" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY,
	"ownerid" BIGINT NOT NULL,
	"type" vdv_media_type NOT NULL,
	"url" VARCHAR(4000) NOT NULL UNIQUE,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_court_follower";
CREATE TABLE "vdv_court_follower" (
	"vdvid" BIGINT NOT NULL,
	"userid" BIGINT NOT NULL,
	"permit" int NOT NULL DEFAULT '0',
	"created" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_user_follower";
CREATE TABLE "vdv_user_follower" (
	"vdvid" BIGINT NOT NULL,
	"followerid" BIGINT NOT NULL,
	"permit" BOOLEAN NOT NULL DEFAULT 'true',
	"created" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_location";
CREATE TABLE "vdv_location" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY,
	"name" VARCHAR(256) NOT NULL UNIQUE,
	"latitude" REAL NOT NULL,
	"longitude" REAL NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "vdv_prop";
CREATE TABLE "vdv_prop" (
	"propid" BIGSERIAL NOT NULL,
	"name" VARCHAR(40) NOT NULL UNIQUE,
	"type" vdv_prop_type NOT NULL
) WITH (
  OIDS=FALSE
);

INSERT INTO vdv_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isopen', 'bool');
INSERT INTO vdv_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isfree', 'bool');
INSERT INTO vdv_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isonair', 'bool');
INSERT INTO vdv_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'price', 'real');
INSERT INTO vdv_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'photo', 'media');
INSERT INTO vdv_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'comment', 'comment');
INSERT INTO vdv_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'like', 'like');


DROP TABLE IF EXISTS "vdv_prop_bool";
CREATE TABLE "vdv_prop_bool" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BOOLEAN NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_prop_int";
CREATE TABLE "vdv_prop_int" (
    "vdvid" BIGSERIAL NOT NULL,
	"propid" BIGSERIAL NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "vdv_prop_real";
CREATE TABLE "vdv_prop_real" (
    "vdvid" BIGSERIAL NOT NULL,
	"propid" BIGSERIAL NOT NULL,
	"value" REAL NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "vdv_prop_media";
CREATE TABLE "vdv_prop_media" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_prop_comment";
CREATE TABLE "vdv_prop_comment" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "vdv_prop_like";
CREATE TABLE "vdv_prop_like" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "vdv_post";
CREATE TABLE "vdv_post" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY,
	"userid" BIGINT NOT NULL,
	"description" VARCHAR(256) NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_comment";
CREATE TABLE "vdv_comment" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"userid" BIGINT NOT NULL,
	"text" TEXT NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_like";
CREATE TABLE "vdv_like" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"userid" BIGINT NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



commit;