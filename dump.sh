

echo "CREATE DATABASE tp;" 	> ./docs/database.sql
echo "USE tp;" 				>> ./docs/database.sql

# Dump the database
# We need to rewrite Universe and NOp to -1
mysqldump -h localhost -u tp -p tp --add-drop-table -Q --skip-disable-keys --skip-add-locks --compatible=ansi,mysql40 --skip-opt \
	| sed -e"s/(0,'tp.server.rules.base.objects.Universe','The Universe/(-1,'tp.server.rules.base.objects.Universe','The Universe/" -e's/\\n/\n/g' >> ./docs/database.sql

# We need to add the fix db stuff
echo "UPDATE object SET id = 0 WHERE name='The Universe';"		>> ./docs/database.sql

echo "CREATE DATABASE tp;" 	> ./docs/database.mysql
echo "USE tp;" 				>> ./docs/database.mysql

# Dump the database
# We need to rewrite Universe and NOp to -1
mysqldump -h localhost -u tp -p tp --add-drop-table -Q --skip-disable-keys --skip-add-locks --skip-opt --create-options \
	| sed -e"s/(0,'tp.server.rules.base.objects.Universe','The Universe/(-1,'tp.server.rules.base.objects.Universe','The Universe/" -e's/\\n/\n/g' >> ./docs/database.mysql

# We need to add the fix db stuff
echo "UPDATE object SET id = 0 WHERE name='The Universe';"		>> ./docs/database.mysql

