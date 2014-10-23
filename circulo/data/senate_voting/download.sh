#!/bin/bash


if [ -z "$1" ]; then 
    echo "Data dir required" 
    exit 0
fi

if [ ! -d "$1" ]; then
    echo "Data dir does not exist"
    exit 0
fi

rsync -avz --delete --delete-excluded --exclude **/text-versions/ govtrack.us::govtrackdata/congress/113/votes/2014 $1
	
rsync -avz --delete --delete-excluded --exclude **/text-versions/ govtrack.us::govtrackdata/congress-legislators/legislators-current.csv $1


