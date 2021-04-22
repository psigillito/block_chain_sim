#!/bin/bash
for((i = 5001; i < 5006; i++))
do
	python3 shutdown.py "$i" &
done

