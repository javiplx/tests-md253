#!/bin/sh
echo "Content-type: text/html"
echo ""
echo "<HTML><HEAD><TITLE>Copyright: Sitecom</TITLE></HEAD><BODY>"
echo "</HEAD><script type=text/javascript>if(document.cookie.indexOf('CD32N:MD-253')<0){ location.replace ('/login.htm');}</script><BODY>"

path=`echo ${QUERY_STRING} | cut '-d&' -f1`

limitpath="/home/PUBLIC/Packages"
if [ $limitpath == $path ]; then
	targetpath=$limitpath
else
	path_len=`echo $path | wc -L`
	lastpath_len=`echo ${path} | awk -F"/" '{print $NF}' | wc -L`
	let targetpath_len=`expr $path_len-$lastpath_len-1`
	targetpath=`echo $path | cut -c-$targetpath_len`
	targetpath=`echo ${targetpath}|sed 's/\%20/\ /g'`
	echo "<a href='javascript:go(\"$targetpath\")'><img src=pictures/_up.jpg height=18 align=top border=0>&nbsp;.&nbsp;.&nbsp;</a><br>"
fi

path=`echo ${path}|sed 's/\%20/\ /g'`
MEDIA_PATH=`/sbin/find "${path}" -maxdepth 1 -type d|/bin/tr " " "^"`

for i in $MEDIA_PATH; do
 i=`echo ${i}|/bin/tr "^" " "`
 [ "${i}" == "${path}" ] && continue

 string=${i##*/}
 echo ${string}|/bin/grep "^\." >/dev/null 2>&1
 [ $? -eq 0 ] && continue

 echo "<div class=\"spacer\"><div style='text-align:left;width:430px;height:25px;float:left;'>"
 echo "<span><a href='javascript:go(\"${i}\")'><img src=pictures/folder.gif height=18 align=top border=0>&nbsp;"${string}"</a></span>"
 echo "</div></div>"
done

PATH_FILE=`/sbin/find "${path}" -maxdepth 1 -type f|/bin/grep "SitecomNas_pkg"|/bin/tr " " "^"`
for FILE in $PATH_FILE; do
 FILE=`echo ${FILE}|/bin/tr "^" " "`
 string=${FILE##*/}

 echo "<div class=\"spacer\"><div style='text-align:left;width:430px;height:25px;float:left;'>"
 echo "<span><a href='javascript:install_pkg(\"${FILE}\")'><img src=pictures/file.gif height=18 align=top border=0>&nbsp;"${string}"</a></span>"
 echo "</div></div>"
done
echo "</BODY></HTML>"

