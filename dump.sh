

echo "CREATE DATABASE tp;" 	> database.sql
echo "USE tp;" 				>> database.sql

# Dump the database
# We need to rewrite Universe and NOp to -1
mysqldump -h localhost -u tp -p tp --add-drop-table -Q --skip-disable-keys --skip-add-locks \
	| sed -e"s/(0,'sobjects.Universe','The Universe/(-1,'sobjects.Universe','The Universe/" >> database.sql

# We need to add the fix db stuff
echo "UPDATE object SET id = 0 WHERE name='The Universe';"		>> database.sql

