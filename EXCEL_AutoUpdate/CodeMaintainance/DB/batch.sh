#! /bin/bash
filelist=$(ls $PWD)

for name in $filelist;do
	if [[ "$name"==*.py ]]; then
		python $name
	else
		echo $name
	fi
done
