apt update
apt install python-alsaaudio python-numpy python-requests python-scipy python-matplotlib rfkill

#we need a dir called /var/recordings:
#home will be /root/hummingpy:

mkdir /var/recordings
mkdir /root/hummingpy

# Install systemd services
cp ./install/humming.service /etc/systemd/system/
cp ./install/hummkill.sh /usr/sbin/
cp ./install/hummon.py /usr/sbin

# Install Network Configuration
cp ./install/interfaces /etc/network/

# Install config and main program file
cp ./install/config.py /root/hummingpy/
cp ./install/humming.py /root/hummingpy/

# make them executable
chmod u+x /root/hummingpy/humming.py
chmod u+x /usr/sbin/hummkill.sh
chmod u+x /usr/sbin/hummon.py

# enable hummingpy and reload systemd init system
systemctl enable humming.service
systemctl daemon-reload
