DROP SEQUENCE IF EXISTS vdv_seq;
CREATE SEQUENCE vdv_seq start with 1 increment by 1;

DROP TYPE IF EXISTS vdv_prop_type CASCADE;
CREATE TYPE vdv_prop_type AS ENUM ('bool', 'int', 'real', 'media', 'comment', 'like', 'location', 'post');

DROP TYPE IF EXISTS vdv_media_type CASCADE;
CREATE TYPE vdv_media_type AS ENUM ('image', 'equipment');

DROP TYPE IF EXISTS vdv_user_admin_type CASCADE;
CREATE TYPE vdv_user_admin_type AS ENUM ('admin', 'super');

DROP TABLE IF EXISTS "vdv_court";
CREATE TABLE "vdv_court" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"ownerid" BIGSERIAL NOT NULL,
	"name" VARCHAR(256) NOT NULL UNIQUE,
	"desc" VARCHAR(4000) NOT NULL DEFAULT '',
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "vdv_user";
CREATE TABLE "vdv_user" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY,
	"username" VARCHAR(256) NOT NULL UNIQUE,
	"e_mail" VARCHAR(256) NOT NULL UNIQUE,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_media";
CREATE TABLE "vdv_media" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY,
	"ownerid" BIGINT NOT NULL,
	"name" VARCHAR(256) NOT NULL DEFAULT '',
	"desc" VARCHAR(4000) NOT NULL DEFAULT '',
	"type" vdv_media_type NOT NULL,
	"url" VARCHAR(4000) NOT NULL UNIQUE,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "vdv_follow";
CREATE TABLE "vdv_follow" (
	"vdvid" BIGINT NOT NULL,
	"followingid" BIGINT NOT NULL,
	"permit" INT NOT NULL DEFAULT 1,
	"is_user" BOOLEAN NOT NULL,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	PRIMARY KEY (vdvid, followingid)
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
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY,
	"name" VARCHAR(40) NOT NULL UNIQUE,
	"type" vdv_prop_type NOT NULL
) WITH (
  OIDS=FALSE
);

INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'private', 'bool');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isopen', 'bool');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isfree', 'bool');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isonair', 'bool');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'price', 'real');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'media', 'media');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'equipment', 'media');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'avatar', 'media');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'comment', 'comment');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'like', 'like');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'location', 'location');
INSERT INTO vdv_prop (vdvid, name, type) VALUES (NEXTVAL('vdv_seq'), 'post', 'post');

DROP TABLE IF EXISTS "vdv_prop_bool";
CREATE TABLE "vdv_prop_bool" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BOOLEAN NOT NULL,
	PRIMARY KEY (vdvid, propid, value)
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_prop_int";
CREATE TABLE "vdv_prop_int" (
    "vdvid" BIGSERIAL NOT NULL,
	"propid" BIGSERIAL NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (vdvid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "vdv_prop_real";
CREATE TABLE "vdv_prop_real" (
    "vdvid" BIGSERIAL NOT NULL,
	"propid" BIGSERIAL NOT NULL,
	"value" REAL NOT NULL,
	PRIMARY KEY (vdvid, propid, value)
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "vdv_prop_media";
CREATE TABLE "vdv_prop_media" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (vdvid, propid, value)
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_prop_comment";
CREATE TABLE "vdv_prop_comment" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (vdvid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "vdv_prop_like";
CREATE TABLE "vdv_prop_like" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL,
	PRIMARY KEY (vdvid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "vdv_prop_location";
CREATE TABLE "vdv_prop_location" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (vdvid, propid, value)
) WITH (
  OIDS=FALSE
);

DROP TABLE IF EXISTS "vdv_prop_post";
CREATE TABLE "vdv_prop_post" (
	"vdvid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BIGINT NOT NULL,
	PRIMARY KEY (vdvid, propid, value)
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
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
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


DROP TABLE IF EXISTS "vdv_user_admin";
CREATE TABLE "vdv_user_admin" (
	"vdvid" BIGSERIAL NOT NULL PRIMARY KEY,
	"userid" BIGINT NOT NULL,
	"level" vdv_user_admin_type NOT NULL
) WITH (
	OIDS=FALSE
);

commit;