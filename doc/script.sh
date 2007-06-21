#! /bin/sh

SQL='sqlite3 -header testing.db'

echo "Example 1\n-------------------------------------------"
rm testing.db
$SQL "
	CREATE TABLE object (
			modtime INTEGER NOT NULL, 
			id      INTEGER NOT NULL, 
			name    VARCHAR(255) NOT NULL
	);
	INSERT INTO object VALUES (0, 1, 'Object 1');
	INSERT INTO object VALUES (0, 2, 'Object 2');
	INSERT INTO object VALUES (1, 1, 'New Object 1');"

echo
echo "The final universe view."
$SQL 'SELECT MAX(modtime),name FROM object GROUP BY id;'
echo
echo "The universe view at turn 0."
$SQL 'SELECT MAX(modtime),name FROM object WHERE modtime <= 0 GROUP BY id;'

echo
echo
echo "Example 2\n-------------------------------------------"
rm testing.db
$SQL "
	CREATE TABLE object (
		rowid   INTEGER NOT NULL,
		modtime INTEGER NOT NULL, 
		id      INTEGER NOT NULL, 
		name    VARCHAR(255) NOT NULL,
        PRIMARY KEY (rowid) 
	);

	CREATE TABLE view (
        playerid  INTEGER NOT NULL, 
		modtime   INTEGER NOT NULL,
		rowid     INTEGER NOT NULL,
		PRIMARY KEY (playerid, rowid),
         FOREIGN KEY(rowid) REFERENCES object (rowid)
	);

	BEGIN;

	INSERT INTO object VALUES (0, 0, 1, 'Object 1');
	INSERT INTO object VALUES (1, 0, 2, 'Object 2');

	INSERT INTO view VALUES (0, 0, (SELECT MAX(rowid) FROM object WHERE id=1));

	INSERT INTO object VALUES (2, 1, 1, 'New Name Object 1');
	INSERT INTO object VALUES (3, 1, 3, 'New Object');

	INSERT INTO view VALUES (0, 1, (SELECT MAX(rowid) FROM object WHERE id=1));
	INSERT INTO view VALUES (0, 1, (SELECT MAX(rowid) FROM object WHERE id=2));

	INSERT INTO object VALUES (4, 2, 1, 'Another Name Object 1');
	INSERT INTO object VALUES (5, 2, 4, 'New Object 2');

	INSERT INTO view VALUES (0, 2, (SELECT MAX(rowid) FROM object WHERE id=4));

	COMMIT;
"

echo
echo "The final universe view."
$SQL "
	SELECT
		MAX(view.modtime), object.name 
	FROM
		view
	JOIN
		object ON view.rowid = object.rowid
	WHERE
		view.playerid = 0
	GROUP BY 
		object.id;"

echo
echo "The view at turn 0."
$SQL "
	SELECT
		MAX(view.modtime), object.name 
	FROM
		view
	JOIN
		object ON view.rowid = object.rowid
	WHERE
		view.playerid = 0 AND view.modtime >= 0
	GROUP BY 
		object.id;"


