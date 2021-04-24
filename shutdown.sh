#!/bin/bash
for((i = $1; i <= ($1 + $2); i++))
do
	python3 shutdown.py "$i" &
done

