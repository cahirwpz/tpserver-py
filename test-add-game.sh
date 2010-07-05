#!/bin/sh

NAME=$1
RULESET=$2

NAME=${NAME:=tp}
RULESET=${RULESET:=minisec}

./tpserver-py-tool <<EOF
game add $NAME $NAME $RULESET admin@localhost foobar
quit
EOF
