#!/bin/sh

RULESET=$1
GAME=$2
USER=$3
PASSWORD=$4

RULESET=${RULESET:=minisec}
GAME=${NAME:=tp}
USER=${USER:=test}
PASSWORD=${PASSWORD:=test}

./tpserver-py-tool <<EOF
game add $GAME $GAME $RULESET admin@localhost foobar
game use $GAME
player add $USER $PASSWORD
populate 666 5 10 5 10
quit
quit
EOF
