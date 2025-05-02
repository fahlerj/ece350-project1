#!/bin/bash

echo "This will install the service file to the system"
set -x

dest_dir="/opt/ece350_project"

project_py_file="project_jfahler_chooks.py"

chmod 777 $project_py_file
sudo rsync -av $project_py_file $dest_dir/

# Update user-specific values
sed -i s,REPLACE_USER,`whoami`,g ./start_temp.service
sed -i s,REPLACE_DIR,$dest_dir,g ./start_temp.service

# Install the service file
sudo cp -av ./start_temp.service /lib/systemd/system/

# Reload systemd to re-read new service
sudo systemctl daemon-reload

# Start the service
sudo systemctl start start_temp.service

# Enable the service on boot
sudo systemctl enable start_temp.service
