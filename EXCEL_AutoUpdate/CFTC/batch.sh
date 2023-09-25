#! /bin/bash
filelist=$(ls /home/targets/autocommit/EXCEL_AutoUpdate/CFTC)

for name in $filelist;do
	if [[ "$name"==*.py ]]; then
		echo $name
	else
		echo $name
	fi
done
