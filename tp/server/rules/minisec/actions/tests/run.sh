#! /bin/sh

for FILE in battle*; do
	if echo "$FILE" | grep -q '.xml$'; then 
		continue
	else
		python ../FleetCombat.py $FILE $FILE.xml
	fi
done


