#!/bin/sh

NAME=$1 

./tpserver-py-tool <<EOF
game use $NAME 
populate 666 5 10 5 10
quit
quit
EOF
