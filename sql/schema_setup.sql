-- DATABASE SCHEMA SETUP
-- PROJECT: Indie Market Strategy
-- Database: PostgreSQL

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

-- Game data
CREATE TABLE game_info (
	id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	game_id integer NOT NULL UNIQUE,
	name text NOT NULL,
	price real NOT NULL,
	rating real NOT NULL,
	release date NOT NULL,
	follows integer NOT NULL,
	reviews integer NOT NULL,
	peak integer NOT NULL
);

-- Game Playtime in Minutes
CREATE TABLE play_time (
	id integer GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
	game_id integer,
	game_name text,
	avg_playtime_minutes integer,
	median_playtime_minutes integer
);
