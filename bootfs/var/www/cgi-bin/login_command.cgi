#!/bin/sh

uid_old=`echo ${QUERY_STRING}|/bin/awk -F\& '{print $(NF-2)}'`
sum_old=`echo ${QUERY_STRING}|/bin/awk -F\& '{print $(NF-1)}'`
oldfile="/tmp/ck_${uid_old}_${sum_old}"
if [ -f ${oldfile} ]; then
	echo "OK"
else
	echo "Fail"
fi
