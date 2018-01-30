CREATE TABLE IF NOT EXISTS Posts (
	id integer primary key autoincrement not null,
	name text,
	author_id integer not null,
	text text,
	time datetime DEFAULT (datetime('now','localtime'))
);

CREATE TABLE IF NOT EXISTS Users (
	id integer primary key autoincrement not null,
	name text,
	password text,
	posts text
);

