#!/bin/bash -e

#ctx logger info "Installing HAProxy"

#OS=$(uname -a | grep Ubuntu)
#ctx logger info "OS is = ${OS}"
#if [[ $OS != '' ]]; then
#    ctx logger info "Installed HAProxy on Ubuntu"
#    sudo apt-get update
#    sudo apt-get -y install haproxy
#    sudo /bin/sed -i s/ENABLED=0/ENABLED=1/ /etc/default/haproxy
#else

ctx logger info "Installed HAProxy on Centos"
#sudo yum update -y
sudo yum -y install haproxy
sudo mv /etc/haproxy/haproxy.cfg  /etc/haproxy/haproxy.cfg.save

#fi

ctx logger info "Installed HAProxy"
