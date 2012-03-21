#!/bin/bash

# Apt-install various things necessary for Ruby, guest additions,
# etc., and remove optional things to trim down the machine.
apt-get -y update
apt-get -y remove apparmor
apt-get -y install linux-headers-$(uname -r) build-essential
apt-get -y install zlib1g zlib1g-dev libxml2 libxml2-dev libxslt-dev libssl-dev openssl libreadline5-dev
apt-get clean

# Remove this file to avoid dhclient issues with networking
rm -f /etc/udev/rules.d/70-persistent-net.rules

# Setup sudo to allow no-password sudo for "admin". Additionally,
# make "admin" an exempt group so that the PATH is inherited.
cp /etc/sudoers /etc/sudoers.orig
sed -i -e '/Defaults\s\+env_reset/a Defaults\texempt_group=admin' /etc/sudoers
sed -i -e 's/%admin ALL=(ALL) ALL/%admin ALL=NOPASSWD:ALL/g' /etc/sudoers

# Configure SSH specifically:
# This tells SSH not to look up the remote hostname for SSHing. This
# speeds up connection and helps when you're connecting with no outside
# internet connection.
echo 'UseDNS no' >> /etc/ssh/sshd_config

# Install NFS client
apt-get -y install nfs-common

# Install insecure Vagrant SSH keys
mkdir /home/vagrant/.ssh
chmod 700 /home/vagrant/.ssh
cd /home/vagrant/.ssh
wget --no-check-certificate 'http://github.com/mitchellh/vagrant/raw/master/keys/vagrant.pub' -O authorized_keys
chown -R vagrant /home/vagrant/.ssh

# Install VirtualBox guest additions
VBOX_VERSION=$(cat /home/vagrant/.vbox_version)
cd /tmp
wget http://download.virtualbox.org/virtualbox/$VBOX_VERSION/VBoxGuestAdditions_$VBOX_VERSION.iso
mount -o loop VBoxGuestAdditions_$VBOX_VERSION.iso /mnt
sh /mnt/VBoxLinuxAdditions.run
umount /mnt
rm VBoxGuestAdditions_$VBOX_VERSION.iso

# Remove items used for building, since they aren't needed anymore
apt-get -y remove linux-headers-$(uname -r) build-essential
apt-get -y autoremove

# Zero free space to aid VM compression
dd if=/dev/zero of=/EMPTY bs=1M
rm -f /EMPTY

# Removing leftover leases and persistent rules
echo "cleaning up dhcp leases"
rm /var/lib/dhcp3/*

# Make sure Udev doesn't block our network
# http://6.ptmc.org/?p=164
echo "cleaning up udev rules"
rm /etc/udev/rules.d/70-persistent-net.rules
mkdir /etc/udev/rules.d/70-persistent-net.rules
rm -rf /dev/.udev/
rm /lib/udev/rules.d/75-persistent-net-generator.rules

echo "Adding a 2 sec delay to the interface up, to make the dhclient happy"
echo "pre-up sleep 2" >> /etc/network/interfaces

# Fix /etc/hosts by removing the 127.0.1.1 line and then adding
# a new one after the localhost line
sed -i -e '/^127\.0\.1\.1/d' /etc/hosts
sed -i -e "/^127\.0\.0\.1/a 127.0.1.1\t`hostname`" /etc/hosts


# Make sure we have a build environment, 
apt-get -y install subversion git mercurial # version control
apt-get -y install patchutils colordiff # development general
apt-get -y install python-py # Translate development
apt-get -y install autoconf2.13 zip unzip yasm # Mozilla langpack building
apt-get -y install vim # edit files
apt-get -y install gettext python-levenshtein python-lxml # msgcat and friends

# Mozilla compare-locales
apt-get -y install python-pip 
easy_install -U compare-locales

# SSH customisations
cp ~/.ssh/ssh_host/config ~/.ssh
#cp ~/.ssh/ssh_host/id_rsa ~/.ssh/id_rsa

exit
