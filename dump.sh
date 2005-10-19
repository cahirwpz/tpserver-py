

echo "CREATE DATABASE tp;" 	> ./db/database.sql
echo "USE tp;" 				>> ./db/database.sql

# Dump the database
# We need to rewrite Universe and NOp to -1
mysqldump -h localhost -u tp -p tp --add-drop-table -Q --skip-disable-keys --skip-add-locks --compatible=ansi,mysql40 --skip-opt \
	| sed -e"s/(0,'sobjects.Universe','The Universe/(-1,'sobjects.Universe','The Universe/" -e's/\\n/\n/g' >> ./db/database.sql

# We need to add the fix db stuff
echo "UPDATE object SET id = 0 WHERE name='The Universe';"		>> ./db/database.sql

echo "CREATE DATABASE tp;" 	> ./db/database.mysql
echo "USE tp;" 				>> ./db/database.mysql

# Dump the database
# We need to rewrite Universe and NOp to -1
mysqldump -h localhost -u tp -p tp --add-drop-table -Q --skip-disable-keys --skip-add-locks --compatible=mysql40 --skip-opt --create-options \
	| sed -e"s/(0,'sobjects.Universe','The Universe/(-1,'sobjects.Universe','The Universe/" -e's/\\n/\n/g' >> ./db/database.mysql

# We need to add the fix db stuff
echo "UPDATE object SET id = 0 WHERE name='The Universe';"		>> ./db/database.mysql

