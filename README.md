# lxcSnapshot
## Work in Progress
Simple tool to snapshot LXC containers on Incus and backup/restore them offside

**Install**<br>
Make sure incus is already installed.<br>
```
curl -so- https://raw.githubusercontent.com/Ne00n/lxcSnap/master/install.sh | bash -s
```

**Usage**<br>
```
lxcsnap set endpoint <master.mydomain.com> <filer.mydomain.com>
lxcsnap set endpoint <master/filer.mydomain.com>
lxcsnap set auth <user> <pw>
lxcsnap create mahContainer
lxcsnap create mahContainer 7d
lxcsnap list mahContainer
lxcsnap restore mahContainer
lxcsnap update
```

**Storage Server**<br>
lxcSnap uses [Seaweedfs](https://github.com/seaweedfs/seaweedfs).<br>
Getting a Seaweedfs server up and running as as simple as.<br>
```
wget https://github.com/seaweedfs/seaweedfs/releases/download/3.67/linux_amd64.tar.gz
tar xvf linux_amd64.tar.gz
mkdir data
./weed server -dir=data -ip=127.0.0.1
```

**Reverse Proxy**<br>
Seaweedfs doesn't support any authentication on the master server, so we have to do our own.<br>
A reverse proxy will do.<br>
```
apt-get install nginx apache2-utils -y
```
vHost example config
```
server {
    listen 80;
    server_name mahstorage.com;
    client_max_body_size 100G;

    location / {
        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:9333;
        proxy_set_header Host $host;
    }
}
```
You can generate the .htpassword with<br>
```
htpasswd -c /etc/nginx/.htpasswd <user>
```