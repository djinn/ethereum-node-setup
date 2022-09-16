#!/bin/bash -

sudo yum update -y
sudo mkdir /ethereum
sudo yum install -y btrfs-progs uuid
sudo amazon-linux-extras install -y epel
sudo yum install -y supervisor
sudo mkfs.btrfs /dev/sdf
sudo su -c 'echo "`blkid /dev/sdf|cut -f2 -d" "` /ethereum btrfs compress=zstd:15 0 1" >> /etc/fstab'
sudo mount /ethereum 
sudo chown -R ec2-user:ec2-user /ethereum
curl https://gethstore.blob.core.windows.net/builds/geth-linux-arm64-1.10.25-69568c55.tar.gz|tar -zx && sudo cp geth*/geth /usr/local/bin
sudo su -c  'cat > /etc/supervisord.d/geth.ini <<EOF 
[program:geth]
user=ec2-user
command=/usr/local/bin/geth  --datadir /ethereum 
autostart=true  
autorestart=true  
stderr_logfile=/var/log/supervisor/geth.err.log  
stdout_logfile=/var/log/supervisor/geth.out.log  
EOF'
sudo systemctl daemon-reload
sudo systemctl start supervisord.service
