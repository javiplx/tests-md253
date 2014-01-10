#!/bin/sh
PATH=/bin:/sbin:/usr/bin:/usr/sbin
export PATH

mode=$1

. /usr/libexec/modules/modules.conf

XFS_QUOTA=/usr/local/xfsprogs/xfs_quota
TWONKY_PKGPATH=/usr/local/install/Twonkymedia

PASSWD=/etc/passwd
SLEEP=1
SHARE_PATH=/home

service_rebuild_stop

echo "hdd1 blue clear" > /proc/mp_leds
echo "hdd2 blue clear" > /proc/mp_leds
echo "hdd1 red clear" > /proc/mp_leds
echo "hdd2 red clear" > /proc/mp_leds
echo "hdd1 red set" > /proc/mp_leds
echo "hdd2 red set" > /proc/mp_leds

service_stop
[ -d ${TWONKY_PKGPATH} ] && {
 ${TWONKY_PKGPATH}/scripts/twonkymedia/twonkymedia.sh stop
}
service_package_manager "Service&stop"

/bin/sleep $SLEEP
/bin/killall udevd >/dev/null 2>&1
/bin/sleep $SLEEP

SHARE_PATH_TREE=`/bin/df|/bin/grep "/home/"|/bin/awk '{print $1}'`
for disk in $SHARE_PATH_TREE; do
 disk=${disk##*/}
 /etc/sysconfig/system-script/umount $disk
done

Directory="PUBLIC Media BitTorrent"
[ -d /tmp/ftpaccess ] || /bin/mkdir -p /tmp/ftpaccess
for i in $Directory; do
 /bin/cp -af ${SHARE_PATH}/${i}/.ftpaccess /tmp/ftpaccess/${i}
done

/bin/umount -l /dev/sda1 >/dev/null 2>&1
/bin/umount -l /dev/sdb1 >/dev/null 2>&1

/bin/umount -l /dev/md1 >/dev/null 2>&1
/usr/bin/mdadm --stop /dev/md1 >/dev/null 2>&1

service_create_partition ${mode} >/dev/null 2>&1

/bin/sleep $SLEEP

cat /dev/null > /etc/mdadm.conf
/usr/bin/mdadm --zero-superblock /dev/sda1
/usr/bin/mdadm --zero-superblock /dev/sdb1
/usr/bin/mdadm --create /dev/md1 --raid-devices=2 --level=${mode} --run /dev/sd[a-b]1 --assume-clean >/dev/null 2>&1
/usr/local/xfsprogs/mkfs.xfs -f /dev/md1 >/dev/null 2>&1
/usr/bin/mdadm -D -s >> /etc/mdadm.conf

echo "hdd1 blue clear" > /proc/mp_leds
echo "hdd2 blue clear" > /proc/mp_leds
echo "hdd1 red clear" > /proc/mp_leds
echo "hdd2 red clear" > /proc/mp_leds

/bin/mount -t xfs -o uquota /dev/md1 ${SHARE_PATH}
[ $? -eq 0 ] && {
 /bin/logger "$0 - Drive Mount Succeed"
 echo "hdd1 blue set" > /proc/mp_leds
 echo "hdd2 blue set" > /proc/mp_leds
 } || {
 /bin/logger "$0 - Drive Mount Failed"
 echo "hdd1 red set" > /proc/mp_leds
 echo "hdd2 red set" > /proc/mp_leds
 }

USER=`/bin/awk -F: /:500:/'{print $1}' ${PASSWD}`
NOBODY=`/bin/awk -F: /^nobody:/'{print $5}' ${PASSWD}|/bin/sed 's/\ //g'`
[ "$NOBODY" == "nobody" ] || {
 bhard=`echo ${NOBODY}|/bin/awk -F, '{print $2}'|/bin/sed 's/\ //g'`
 ${XFS_QUOTA} -x -c "limit -u bsoft=${bhard}g bhard=${bhard}g 99" /home
 }

for user in ${USER}; do
 USER_UID=`/bin/awk -F: /^${user}:/'{print $3}' ${PASSWD}`
 bhard=`/bin/awk -F: /^${user}:/'{print $5}' ${PASSWD}|\
        /bin/awk -F, '{print $2}'|/bin/sed 's/\ //g'`
 [ "$bhard" == "0" ] && bhard=999999999

 ${XFS_QUOTA} -x -c "limit -u bsoft=${bhard}g bhard=${bhard}g ${USER_UID}" ${SHARE_PATH}
done

for disk in $SHARE_PATH_TREE; do
 disk=${disk##*/}
 [ "$disk" == "sdb1" ] && continue
 /etc/sysconfig/system-script/mount $disk
done

service_smb_modify_conf
service_daapd_modify_config

for i in $Directory; do
 /bin/cp -af /tmp/ftpaccess/${i} ${SHARE_PATH}/${i}/.ftpaccess
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
