#!/bin/sh

set -e

if ! test -d /opt ; then
    echo
    echo "Bad firmware, no /opt link"
    echo
    exit
    fi

feed=http://ks301030.kimsufi.com/md253/optware

ipk_name=$( wget -qO- $feed/Packages.gz | gunzip | awk '/^Filename: ipkg-opt/ {print $2}' )
wget -qO- $feed/$ipk_name | tar -xOz ./data.tar.gz | tar -xz -C /
echo "src/gz optware ${feed}" >> /opt/etc/ipkg.conf
mkdir /opt/lib/ipkg

cat <<EOF > /opt/lib/ipkg/status
Package: ipkg-opt
Version: 0.99.163-10
Status: install user installed
Architecture: arm 

EOF

echo "optware feed installed"

