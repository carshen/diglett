#!/bin/bash

# Leech on school resources bwahahahahahaha.
# Usage: ./emailer.sh 'subject' 'email address' seconds

if [ $# -ne 3 ]; then
	echo "Usage: ./emailer.sh 'subject' 'email address' seconds"
	exit 1
fi

while true
do
	# Don't forget to chmod u+x send_flashcard.py.
	./send_flashcard.py "$1" "$2"
	sleep "$3"
done
