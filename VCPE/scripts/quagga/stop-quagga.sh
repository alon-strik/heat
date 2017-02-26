#!/bin/bash

set -e

ctx logger info  "Stoping Quagga..."
sudo /etc/init.d/quagga stop
