#!/bin/sh
echo -e "Content-type: text/html"\\r
echo -e ""\\r
echo -e "<HTML><HEAD><TITLE>Sample CGI Output2</TITLE></HEAD><BODY>"\\r

. /usr/libexec/modules/modules.conf
PASSWD=/etc/passwd
CONF_PATH=/etc/sysconfig/config
SMB_SHARES_CONF=${CONF_PATH}/smb/shares.inc
SMB_HOST_CONF=${CONF_PATH}/smb/host.inc
IFCFG=${CONF_PATH}/ifcfg-eth0
IFCFG_DEFAULT=${CONF_PATH}/ifcfg-eth0.default
replaceFile=/bin/replaceFile

scsi_list=/etc/sysconfig/config/scsi.list

format_hdd=/var/www/cgi-bin/format.sh
SingleFormat=/var/www/cgi-bin/SingleFormat.sh
XFS_QUOTA=/usr/local/xfsprogs/xfs_quota
func=`echo ${QUERY_STRING} | cut '-d&' -f1`


PKG_Folder=/usr/local/install
PACKAGE=${PKG_Folder}/package
PKGPATH=/usr/local/install


case ${func} in
"SetExecTable")
	Value=`echo ${QUERY_STRING}|/bin/cut '-d&' -f2|/bin/sed 's/\%20/\ /g'`
	$Value
	;;
"check_pkg")
	if [ -d ${PKG_Folder} ]; then
		cd ${PKG_Folder}
		PKG=`echo ${QUERY_STRING}|/bin/cut '-d&' -f2`
		PKG_IPK=`/bin/basename $PKG | /bin/awk -F"_" '{print $3}'`

		cat package | grep ${PKG_IPK} > /dev/null

		if [ $? -eq 0 ]; then
			echo -e "exist"\\r
		else
			echo -e "null"\\r
		fi
	else
		echo -e "no_devic1e"\\r
	fi 
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
"PackageAction")
  QUERY_STRING=`echo ${QUERY_STRING} | sed 's/\%5E/\^/'`
  action=`echo ${QUERY_STRING} | cut '-d&' -f2`
  service_package_manager ${QUERY_STRING} ${action}
  ;;
*)
    QUERY_STRING=`echo ${QUERY_STRING} | sed 's/\%5E/\^/'`
	echo -e "${QUERY_STRING} ${REQUEST_METHOD}"\\r
	;;
esac

echo -e "</BODY></HTML>"\\r
