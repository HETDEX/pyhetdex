#!/bin/bash
# remove the empty .coverage files to avoid issues when combining the coverage
# results

for i in .coverage*
do
    if [ ! -s $i ]
    then
        rm $i
    fi
done
