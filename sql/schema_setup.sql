-- DATABASE SCHEMA SETUP
-- PROJECT: Indie Market Strategy
-- Database: PostgreSQL


-- ==========================================
-- 1. REFERENCE TABLES (Create these FIRST)
-- ==========================================
-- Tag (Official Steam Tags)
CREATE TABLE tag (
	id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	tag_id integer NOT NULL, 
	tag_name varchar(50) NOT NULL,
	steam_tags integer NOT NULL,
	is_game_genre BOOLEAN NOT NULL
);

-- Game Id
CREATE TABLE game_id (
	id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	game_id integer NOT NULL UNIQUE,
	name text NOT NULL
);

-- ==========================================
-- 2. DIMENSION TABLES (Create these SECOND)
-- ==========================================
-- Game data
CREATE TABLE game_info (
	id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	game_id integer NOT NULL,
	name text,
	price real,
	rating real,
	release date,
	follows integer,
	reviews integer,
	peak integer
	CONSTRAINT fk_game_source FOREIGN KEY (game_id) 
		REFERENCES game_id (game_id)
);

-- Game Playtime in Minutes
CREATE TABLE play_time (
	id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	game_id integer,
	name text,
	avg_playtime_minutes integer,
	median_playtime_minutes integer
	CONSTRAINT fk_game_source FOREIGN KEY (game_id) 
		REFERENCES game_id (game_id)
);

-- Game with their Tags
CREATE TABLE game_tag (
	id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	game_id integer,
	name text,
	tag_id integer
	CONSTRAINT fk_game_source FOREIGN KEY (game_id) 
		REFERENCES game_id (game_id)
	CONSTRAINT fk_game_source_tag FOREIGN KEY (tag_id) 
		REFERENCES tag (tag_id)
);
