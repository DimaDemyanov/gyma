DROP SEQUENCE vdv_seq;
create SEQUENCE vdv_seq start with 1 increment by 1;

DROP TYPE IF EXISTS vdv_prop_type;
CREATE TYPE vdv_prop_type AS ENUM ('bool', 'numeric', 'media', 'comment', 'like');

DROP TABLE IF EXISTS "vdv_court";
CREATE TABLE "vdv_court" (
	"courtid" BIGSERIAL NOT NULL PRIMARY KEY ,
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
	"userid" BIGSERIAL NOT NULL PRIMARY KEY,
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
	"mediaid" BIGSERIAL NOT NULL PRIMARY KEY,
	"ownerid" BIGINT NOT NULL,
	"type" int NOT NULL,
	"url" VARCHAR(256) NOT NULL UNIQUE,
	"created" TIMESTAMP WITH TIME ZONE NOT NULL,
	"updated" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_court_follower";
CREATE TABLE "vdv_court_follower" (
	"courtid" BIGINT NOT NULL,
	"userid" BIGINT NOT NULL,
	"permit" int NOT NULL DEFAULT '0',
	"timestamp" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_user_follower";
CREATE TABLE "vdv_user_follower" (
	"userid" BIGINT NOT NULL,
	"followerid" BIGINT NOT NULL,
	"permit" BOOLEAN NOT NULL DEFAULT 'true',
	"timestamp" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_location";
CREATE TABLE "vdv_location" (
	"locid" BIGSERIAL NOT NULL PRIMARY KEY,
	"name" VARCHAR(256) NOT NULL UNIQUE,
	"GPS" POINT NOT NULL
) WITH (
  OIDS=FALSE
);


DROP TABLE IF EXISTS "vdv_court_prop";
CREATE TABLE "vdv_court_prop" (
	"propid" BIGSERIAL NOT NULL,
	"name" VARCHAR(40) NOT NULL UNIQUE,
	"type" vdv_prop_type NOT NULL
) WITH (
  OIDS=FALSE
);

INSERT INTO vdv_court_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isopen', 'bool');
INSERT INTO vdv_court_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isfree', 'bool');
INSERT INTO vdv_court_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'isonair', 'bool');
INSERT INTO vdv_court_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'price', 'numeric');
INSERT INTO vdv_court_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'photo', 'media');
INSERT INTO vdv_court_prop (propid, name, type) VALUES (NEXTVAL('vdv_seq'), 'review', 'comment');


DROP TABLE IF EXISTS "vdv_court_prop_bool";
CREATE TABLE "vdv_court_prop_bool" (
	"courtid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" BOOLEAN NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_court_prop_numeric";
CREATE TABLE "vdv_court_prop_numeric" (
	"propid" BIGSERIAL NOT NULL,
	"value" NUMERIC(20) NOT NULL,
	"courtid" BIGSERIAL NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_court_prop_media";
CREATE TABLE "vdv_court_prop_media" (
	"courtid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_court_prop_comment";
CREATE TABLE "vdv_court_prop_comment" (
	"courtid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_post";
CREATE TABLE "vdv_post" (
	"postid" BIGSERIAL NOT NULL PRIMARY KEY,
	"userid" BIGINT NOT NULL,
	"description" VARCHAR(256) NOT NULL,
	"timestamp" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_comment";
CREATE TABLE "vdv_comment" (
	"commentid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"userid" BIGINT NOT NULL,
	"text" TEXT NOT NULL,
	"timestamp" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_post_prop";
CREATE TABLE "vdv_post_prop" (
	"propid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"name" VARCHAR(40) NOT NULL UNIQUE,
	"type" vdv_prop_type NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_like";
CREATE TABLE "vdv_like" (
	"likeid" BIGSERIAL NOT NULL PRIMARY KEY ,
	"userid" BIGINT NOT NULL,
	"timestamp" TIMESTAMP WITH TIME ZONE NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_court_prop_like";
CREATE TABLE "vdv_court_prop_like" (
	"courtid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_post_like";
CREATE TABLE "vdv_post_like" (
	"postid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_post_media";
CREATE TABLE "vdv_post_media" (
	"postid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);



DROP TABLE IF EXISTS "vdv_post_comment";
CREATE TABLE "vdv_post_comment" (
	"postid" BIGINT NOT NULL,
	"propid" BIGINT NOT NULL,
	"value" INT NOT NULL
) WITH (
  OIDS=FALSE
);

commit;