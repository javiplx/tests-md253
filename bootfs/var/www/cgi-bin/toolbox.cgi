#!/bin/sh
echo "Content-type: text/html"
echo ""
echo "<HTML><HEAD><TITLE>Sample CGI Output</TITLE></HEAD><BODY>"

. /usr/libexec/modules/modules.conf
func=`echo ${QUERY_STRING} | cut '-d&' -f1`
firmware=`echo ${QUERY_STRING} | cut '-d&' -f2`
VERSION=/etc/sysconfig/config/version
targetpath=${firmware%/*}
tempFolder=$targetpath"/.tempByMapower"
PKG_Folder=/usr/local/install
PACKAGE=${PKG_Folder}/package

versionset(){
for i in $1; do
 eval x=\\$i
 export $x
done
}

case ${func} in
 Reboot)
  /bin/ls >/dev/null 2>&1
  /bin/reboot
  ;;
 Reset_2_Def)
  /bin/rm -f /etc/sysconfig/config/finish
  SHARE_PATH=/home
  FOLDER=`/bin/find "${SHARE_PATH}" -maxdepth 1 -type d|/bin/tr " " "^"`
  for i in ${FOLDER}; do
   i=`echo ${i}|/bin/tr "^" " "`
   [ "${i}" == "${SHARE_PATH}" ] && continue

   name=${i##*/}
   echo ${name}|/bin/grep "^\." >/dev/null 2>&1
   [ $? -eq 0 ] && continue

   /bin/rm -rf ${i}/.ftpaccess
  done
  ;;
 CheckNEW)
  cd /tmp
   /bin/rm -f /tmp/version.xml
  /bin/wget http://portal.sitecom.com/MD-254/v1001/upgrade/version.xml > /tmp/.msg 2>&1
  [ $? -eq 0 ] && {
   VerNum=`/bin/awk -F\" /version/'{print $2}' /tmp/version.xml|/bin/sed 's/\ //g'`

   new=`echo "$VerNum"|/bin/awk -F. '{print "new_a="$1,"new_b="$2,"new_c="$3}'`
   old=`/bin/awk -F_ '{print $2}' ${VERSION}|/bin/sed 's/v//'|/bin/sed 's/[a-z]$//'|\
      /bin/awk -F. '{print "old_a="$1,"old_b="$2,"old_c="$3}'`

   versionset "$new"
   versionset "$old"

   for x in a b c; do
    eval new_num=\$new_$x
    eval old_num=\$old_$x
    [ $new_num -gt $old_num ] && {
     echo "${VerNum}"
     /bin/cp -af /tmp/version.xml /var/www
     break
     }
   done
   /bin/rm -f /tmp/.msg
   } || {
   echo "NoConnect"
   /bin/cat /tmp/.msg|/bin/grep "wget:"|/bin/sed 's/wget:\ //'
   /bin/rm -f /tmp/.msg
   }
  ;;
 DownloadFirmware)
  DELAY_TIME=1
  TimeOut=120
  num=0
  person=0

  cd /tmp
  /bin/rm -f /tmp/*.bin
  /bin/wget ${firmware} > /tmp/.msg 2>&1 &

  # detect timeout
  while true; do
   val=`/bin/cat /tmp/.msg|/bin/grep -v 'Connecting'|/bin/tr '\cM' '\n'|/bin/awk '{print $2}'`
   for i in $val; do
    value_2=$i
   done

   [ "${value_2}" == "100%" ] && {
    [ $person -ge 3 ] && break || {
     person=`expr $person + 1`
     }
    }

   [ "${value_1}" == "${value_2}" ] && {
    [ $num -ge $TimeOut ] && break || {
     /bin/sleep $DELAY_TIME
     num=`expr $num + 1`
     continue
     }
    } || {
    /bin/sleep $DELAY_TIME
    value_1="${value_2}"
    continue
    }
  done

  /bin/cat /tmp/.msg|/bin/grep "100%"|/bin/grep "00:00:00" >/dev/null 2>&1
  [ $? -eq 0 ] && echo "OK" || {
   /bin/killall wget
   echo "NOT"
   }

  /bin/rm -f /tmp/.msg
  ;;
 Decompression)
  # create temp folder
  /bin/rm -rf ${tempFolder}
  /bin/mkdir ${tempFolder}

  # decompression
  cd ${tempFolder}
  /bin/tar xvf $firmware
  ;;
 "Kernel_upgrade")
  # upgrade kernel
  cd $tempFolder
  if [ -f uImage.bin ]; then
   new=`md5sum uImage.bin | awk '{print $1}'`
   old=`cat uImage.md5sum | awk '{print $1}'`
   if [ "$new" == "$old" ]; then
    /bin/flashcp uImage.bin /dev/mtd1
    echo "-finish-"
   else
    echo "error"
   fi
  else
   echo "no"
  fi
  ;;
 "Bootfs_upgrade")
  # upgrade Bootfs
  cd $tempFolder
  if [ -f bootfs.bin ]; then
   new=`md5sum bootfs.bin | awk '{print $1}'`
   old=`cat bootfs.bin.md5sum | awk '{print $1}'`
   if [ "$new" == "$old" ]; then
    /bin/flashcp bootfs.bin /dev/mtd2
    echo "-finish-"
   else
    echo "error"
   fi
  else
   echo "no"
  fi
  ;;
 "FileSystem_upgrade")
  # upgrade FileSystem
  cd $tempFolder
  if [ -f filesystem.bin ]; then
   new=`md5sum filesystem.bin | awk '{print $1}'`
   old=`cat filesystem.bin.md5sum | awk '{print $1}'`
   if [ "$new" == "$old" ]; then
    /bin/flashcp filesystem.bin /dev/mtd3
    echo "-finish-"
   else
    echo "error"
   fi
  else
   echo "no"
  fi
  cd ..
  /bin/rm -rf $tempFolder
  ;;
 "install_pkg")
	# 若沒有須要的目錄，則須先建立
	[ -d /home/PUBLIC/.pkg ] || {
	/bin/mkdir -p /home/PUBLIC/.pkg/lib
	/bin/mkdir -p /home/PUBLIC/.pkg/bin
	}

	# 若沒有須要的User，則須先建立
	PKG_USER="squeeze lp"
	for i in $PKG_USER; do 
	user=`/bin/cat /etc/passwd | grep $i`
	[ "X${user}" == "X" ] && /bin/adduser $i -h /home -H -D -G admin
	done

	# 若 /usr/local/install 存在才執行
	if [ -d ${PKG_Folder} ]; then
		cd ${PKG_Folder}
		# 由 url 第二個參數取得package 名稱
		PKG=`echo ${QUERY_STRING}|/bin/cut '-d&' -f2`
		PKG_IPK=`/bin/basename $PKG | /bin/awk -F"_" '{print $3}'`
		PKG_SCRIPT=${PKG_IPK}/scripts

		# 將package 解壓縮至tmp
		mkdir -p tmp
		cd tmp
		rm -rf $PKG_IPK
		tar zxf $PKG

		# 取得新package 版本
		newVersion=`cat ${PKG_SCRIPT}/INFO | grep "OFF"| awk -F"~" '{print $3}'`

		# 判斷是否有安裝過及版本是否不同
		cd ..
		oldversion=`cat package | grep ${PKG_IPK} | awk -F"~" '{print $3}'`
		if [ "${oldversion}" != "${newVersion}" ]; then
			# oldversion != "" 即須更新版本，先移除舊版本
			if [ "${oldversion}" != "" ]; then
				sh ${PKG_SCRIPT}/start-stop-status del
			fi

			#開始安裝
			cd ${PKG_Folder}
			#刪除原有的，並用新的取代
			rm -rf $PKG_IPK
			mv tmp/$PKG_IPK .

			#再次確認
			PKG_NAME=`/bin/cat ${PKG_SCRIPT}/INFO | /bin/grep "OFF"| /bin/awk -F"~" '{print $2}'`
			[ ${PKG_IPK} != ${PKG_NAME} ] && {
				echo -e "error"\\r
				/bin/rm -rf $PKG_IPK
				return
			}
			#確認所須間是否足夠
			pkg_need_size=`/bin/cat ${PKG_SCRIPT}/INFO | /bin/grep "SIZE"| /bin/awk -F= /SIZE/'{print $2}'`
			hdd_remnant_size=`/bin/df| /bin/grep "/home$"| /bin/awk  '{print $4}'| /bin/sed s/\ //g`
			hdd_remnant_size=`/bin/echo ${hdd_remnant_size}000`

			remnant=$(($hdd_remnant_size-$pkg_need_size)) 
			if [ ${remnant} -ge 0 ]; then
				if [ -d ${PKG_IPK} ]; then
					/bin/cat ${PKG_SCRIPT}/INFO | /bin/grep "OFF" >> ${PACKAGE}
					#判斷若為Twonkymedia則直接啟動
					for pkg in `/bin/cat ${PACKAGE}`; do
						Package=$pkg
						PackageName=`echo "$Package"|/bin/awk -F~ '{print $2}'`
						[ "${PackageName}" == "Twonkymedia" ] && {
							PackageNum=`echo "$Package"|/bin/awk -F~ '{print $1}'`
							String="PackageAction&${PackageName}&${PackageNum}"
							service_package_manager ${String} start
						}
					done
					echo -e "ok"\\r
				else
					echo -e "error"\\r
				fi
			else
				/bin/rm -rf $PKG_IPK
				echo -e "no_remnant_size"\\r
			fi
		else
			echo -e "exist"\\r
		fi
	else
		echo -e "no_device"\\r
	fi 
	;;
 *)
  echo "Hello Mapower ${QUERY_STRING} ${REQUEST_METHOD}"
  ;;
esac

echo "</BODY></HTML>"
