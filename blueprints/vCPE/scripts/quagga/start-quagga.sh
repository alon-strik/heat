#!/bin/bash

set -e

ctx logger info  "Starting Quagga..."
sudo /etc/init.d/quagga start
