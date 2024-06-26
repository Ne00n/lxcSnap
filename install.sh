#!/bin/bash
set -e
if [[ $(id -u) -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi
apt-get install python3 git -y
cd /opt/
git clone https://github.com/Ne00n/lxcSnap.git
cd lxcSnap
git checkout master
useradd lxcSnap -r -d /opt/lxcSnap -s /bin/bash
cp /opt/lxcSnap/configs/config.example.json /opt/lxcSnap/configs/config.json
chown -R lxcSnap:lxcSnap /opt/lxcSnap/
#add wgmesh to /usr/local/bin
cat <<EOF >>/usr/local/bin/lxcsnap
#!/bin/bash
if [[ $(id -u) -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi
su lxcSnap <<EOF2
/opt/lxcSnap/lxcsnap.py \$@
EOF2
EOF
chmod +x /usr/local/bin/lxcSnap
usermod -a -G incus-admin lxcSnap