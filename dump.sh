
# Dump the database
# We need to rewrite Universe and NOp to -1
mysqldump -h localhost -u tp -p tp --add-drop-table -Q \
	| sed -e"s/(0,0,'The Universe/(-1,0,'The Universe/" \
		  -e"s/(0,'Universe/(-1,'Universe/" \
		  -e"s/(0,'NOp/(-1,'NOp/" > database.sql

# We need to add the fix db stuff
echo "UPDATE object SET id = 0 WHERE name='The Universe';"		>> database.sql
echo "UPDATE object_type SET id = 0 WHERE name = 'Universe';"	>> database.sql
echo "UPDATE order_type SET id = 0 WHERE name = 'NOp';"			>> database.sql

