#!/bin/bash

set -e
function install_quagga()
{
    ctx logger info  "Step #2 Installing Quagga components"

    sudo apt-get install quagga quagga-doc -y

    ctx logger info  "Step #3 modify /etc/quagga/daemons"

    sudo sed -i -e "s#zebra=no#zebra=yes#g" /etc/quagga/daemons
    sudo sed -i -e "s#ripd=no#ripd=yes#g" /etc/quagga/daemons
    sudo sed -i -e "s#ospfd=no#ospfd=yes#g" /etc/quagga/daemons

    ctx logger info  "Step #4 create config files"

    sudo cp /usr/share/doc/quagga/examples/zebra.conf.sample /etc/quagga/zebra.conf
    sudo cp /usr/share/doc/quagga/examples/ospfd.conf.sample /etc/quagga/ospfd.conf
    sudo cp /usr/share/doc/quagga/examples/ripd.conf.sample /etc/quagga/ripd.conf

    ctx logger info  "Step #5 set password"

    echo "password password" | sudo tee --append /etc/quagga/zebra.conf
    echo "password password" | sudo tee --append /etc/quagga/ripd.conf
    echo "password password" | sudo tee --append /etc/quagga/ospfd.conf

    ctx logger info  "Step #6 set credentials"

    sudo chown quagga.quaggavty /etc/quagga/*.conf
    sudo chmod 640 /etc/quagga/*.conf

}

function main()
{
    ctx logger info  "Step #1 Update server..."

    sudo apt-get -y update

    install_quagga
    
    ctx logger info  "Step #7 installation done"
}

main
