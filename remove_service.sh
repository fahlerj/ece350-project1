#!/bin/bash

set -x

sudo systemctl stop start_temp.service
sudo systemctl disable start_temp.service
sudo rm -f /lib/systemd/system/start_temp.service
sudo rm -rvf /opt/ece350_project
sudo systemctl daemon-reload
git restore start_temp.service
