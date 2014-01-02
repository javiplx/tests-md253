#!/bin/sh
PATH=/bin:/sbin:/usr/bin:/usr/sbin
export PATH

. /usr/libexec/modules/modules.conf
CONFIG_PATH=/etc/sysconfig/config
SMB_CONF=${CONFIG_PATH}/smb/smb.conf
scsi_list=${CONFIG_PATH}/scsi.list

XFS_QUOTA=/usr/local/xfsprogs/xfs_quota
TWONKY_PKGPATH=/usr/local/install/Twonkymedia

PASSWD=/etc/passwd
SLEEP=1
SHARE_PATH=/home

service_rebuild_stop && \
 service_crond_start

val=`echo $1|/bin/cut '-d_' -f2`
[ "$val" == "0" ] && str=hdd1 || str=hdd2
dev=`echo $1|/bin/cut '-d_' -f1`

echo "${str} blue clear" > /proc/mp_leds
echo "${str} red set" > /proc/mp_leds

service_stop
[ -d ${TWONKY_PKGPATH} ] && {
 ${TWONKY_PKGPATH}/scripts/twonkymedia/twonkymedia.sh stop
}
service_package_manager "Service&stop"

/bin/sleep $SLEEP
/bin/killall udevd >/dev/null 2>&1
/bin/sleep $SLEEP

DiskNum=0
for scsi in SCSI0 SCSI1; do
 MODEL=`/bin/awk -F: /${scsi}/'{print $2}' ${scsi_list}`
 [ "$MODEL" == "" ] && continue || DiskNum=`expr $DiskNum + 1`
  REAL=$scsi
done

SHARE_PATH_TREE=`/bin/df|/bin/grep -v "/home/Disk_2"|\
                 /bin/grep "/home/"|/bin/awk '{print $1}'`

[ -d /tmp/ftpaccess ] || /bin/mkdir -p /tmp/ftpaccess
[ $DiskNum -lt 2 ] || {
 /bin/cp -af ${SHARE_PATH}/Disk_2/.ftpaccess /tmp/ftpaccess/Disk_2
 }

for disk in $SHARE_PATH_TREE; do
 disk=${disk##*/}
 /etc/sysconfig/system-script/umount $disk
done

Directory="PUBLIC Media BitTorrent"
for Dir in $Directory; do
 /bin/cp -af ${SHARE_PATH}/${Dir}/.ftpaccess /tmp/ftpaccess/${Dir}
done

RAID_MODE=`/usr/bin/mdadm -D /dev/md1`
[ "$RAID_MODE" == "" ] && {
 /bin/umount -l /dev/sdb1 >/dev/null 2>&1
 /bin/umount -l /dev/sda1 >/dev/null 2>&1
 } || {
 /bin/umount -l /dev/md1 >/dev/null 2>&1
 /usr/bin/mdadm --stop /dev/md1 >/dev/null 2>&1

 for drive in a b; do
  for num in 1 2; do
   /bin/umount -l /dev/sd${drive}${num} >/dev/null 2>&1
  done
 done
 }

service_create_single_partition ${dev} >/dev/null 2>&1

/bin/sleep $SLEEP

/usr/local/xfsprogs/mkfs.xfs -f /dev/${dev}1 >/dev/null 2>&1

[ $DiskNum -lt 2 ] && {
 echo "${str} blue clear" > /proc/mp_leds
 echo "${str} red clear" > /proc/mp_leds

 /bin/mount -t xfs -o uquota /dev/${dev}1 ${SHARE_PATH}
 [ $? -eq 0 ] &&\
  echo "${str} blue set" > /proc/mp_leds ||\
  echo "${str} red set" > /proc/mp_leds
 } || {
 echo "hdd1 blue clear" > /proc/mp_leds
 echo "hdd1 red clear" > /proc/mp_leds
 echo "hdd2 blue clear" > /proc/mp_leds
 echo "hdd2 red clear" > /proc/mp_leds

 /bin/mount -t xfs -o uquota /dev/sda1 ${SHARE_PATH}
 [ $? -eq 0 ] &&\
  echo "hdd1 blue set" > /proc/mp_leds ||\
  echo "hdd1 red set" > /proc/mp_leds

 [ -d "${SHARE_PATH}/Disk_2" ] || /bin/mkdir -p ${SHARE_PATH}/Disk_2
 /bin/mount -t xfs -o uquota /dev/sdb1 ${SHARE_PATH}/Disk_2
 [ $? -eq 0 ] && {
  echo "hdd2 blue set" > /proc/mp_leds
  /bin/chmod 777 ${SHARE_PATH}/Disk_2
  } || {
  echo "hdd2 red set" > /proc/mp_leds
  /bin/rm -rf ${SHARE_PATH}/Disk_2
  }
 }

/bin/df|/bin/grep "/home/Disk_2" >/dev/null 2>&1
[ $? -eq 0 ] && DISK2STATUS=Yes || DISK2STATUS=No

USER=`/bin/awk -F: /:500:/'{print $1}' ${PASSWD}`
NOBODY=`/bin/awk -F: /^nobody:/'{print $5}' ${PASSWD}|/bin/sed 's/\ //g'`
[ "$NOBODY" == "nobody" ] || {
 bhard=`echo ${NOBODY}|/bin/awk -F, '{print $2}'|/bin/sed 's/\ //g'`
 ${XFS_QUOTA} -x -c "limit -u bsoft=${bhard}g bhard=${bhard}g 99" /home
 [ ${DISK2STATUS} == "Yes" ] &&\
  ${XFS_QUOTA} -x -c "limit -u bsoft=${bhard}g bhard=${bhard}g 99" /home/Disk_2
 }

for user in ${USER}; do
 USER_UID=`/bin/awk -F: /^${user}:/'{print $3}' ${PASSWD}`
 bhard=`/bin/awk -F: /^${user}:/'{print $5}' ${PASSWD}|\
        /bin/awk -F, '{print $2}'|/bin/sed 's/\ //g'`
 [ "$bhard" == "0" ] && bhard=999999999

 ${XFS_QUOTA} -x -c "limit -u bsoft=${bhard}g bhard=${bhard}g ${USER_UID}" ${SHARE_PATH}

 [ ${DISK2STATUS} == "Yes" ] &&\
  ${XFS_QUOTA} -x -c "limit -u bsoft=${bhard}g bhard=${bhard}g ${USER_UID}" ${SHARE_PATH}/Disk_2
done

for disk in $SHARE_PATH_TREE; do
 disk=${disk##*/}
 [ $DiskNum -lt 2 ] || {
  [ "$disk" == "sdb1" ] && continue
  }
 /etc/sysconfig/system-script/mount $disk
done

service_smb_modify_conf
service_daapd_modify_config

[ ${DISK2STATUS} == "Yes" ] || {
 /bin/cp -af /tmp/ftpaccess/Disk_2 ${SHARE_PATH}/Disk_2/.ftpaccess
 }

for Dir in $Directory; do
 /bin/cp -af /tmp/ftpaccess/${Dir} ${SHARE_PATH}/${Dir}/.ftpaccess
done
/bin/rm -rf /tmp/ftpaccess

service_start
[ -d ${TWONKY_PKGPATH} ] && {
 ${TWONKY_PKGPATH}/scripts/twonkymedia/twonkymedia.sh start
}

/bin/mkdir -p /home/.opt

/bin/mkdir -p /home/PUBLIC/Media
/bin/mkdir -p /home/PUBLIC/Packages
/bin/mkdir -p /home/PUBLIC/.pkg/lib
/bin/mkdir -p /home/PUBLIC/.pkg/bin
/bin/chown nobody.nogroup /home/PUBLIC/Media
/bin/chown nobody.nogroup /home/PUBLIC/Packages
/bin/chmod 777 /home/PUBLIC/Media
/bin/chmod 777 /home/PUBLIC/Packages

/bin/udevd --daemon
/bin/logger "$0 - Drive Format Succeed"
