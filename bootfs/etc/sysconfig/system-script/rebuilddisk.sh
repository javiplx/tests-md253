#!/bin/sh
PATH=/bin:/sbin:/usr/bin:/usr/sbin
export PATH

. /usr/libexec/modules/modules.conf
SLEEP=1

/bin/killall udevd >/dev/null 2>&1
/bin/sleep $SLEEP

for disk in sda sdb; do
 MD_STATUS=`/usr/bin/mdadm -D /dev/md1`
 echo "$MD_STATUS"|/bin/grep "$disk" >/dev/null 2>&1
 [ $? -eq 0 ] && {
  active=$disk
  break
  }
done

case ${active} in
 sda)
  str="sda:sdb"
  dev=sdb
  echo "hdd2 blue clear" > /proc/mp_leds
  echo "hdd2 red clear" > /proc/mp_leds
  echo "hdd2 red set" > /proc/mp_leds
  /bin/umount /dev/sdb1
  ;;
 sdb)
  str="sdb:sda"
  dev=sda
  echo "hdd1 blue clear" > /proc/mp_leds
  echo "hdd1 red clear" > /proc/mp_leds
  echo "hdd1 red set" > /proc/mp_leds
  /bin/umount /dev/sda1
  ;;
esac

/usr/bin/mdadm --zero-superblock /dev/${dev}1

service_create_partition_rebuild ${str}

case ${active} in
 sda)
  /usr/bin/mdadm -a /dev/md1 /dev/sdb1
  ;;
 sdb)
  /usr/bin/mdadm -a /dev/md1 /dev/sda1
  ;;
esac

service_rebuild_start
