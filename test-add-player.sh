#!/bin/sh

GAME=$1
USER=$2 
PASSWORD=$3

./tpserver-py-tool <<EOF
game use $GAME
player add $USER $PASSWORD
quit
quit
EOF
