#!/bin/bash

set -e

REPO_URL="https://github.com/Searchforsomething/tcp-chat.git"
CLONE_DIR="$HOME/tcp-chat"

if [ ! -d "$CLONE_DIR" ]; then
    git clone "$REPO_URL" "$CLONE_DIR"
else
    echo "Repository is already cloned to $CLONE_DIR"
fi

cd "$CLONE_DIR"

sudo dnf -y update
sudo dnf -y install rpm-build rpmdevtools

rpmdev-setuptree

mkdir -p /tmp/chatserver-1.0
cp -r server/chatserver/* /tmp/chatserver-1.0/
tar czf ~/rpmbuild/SOURCES/chatserver-1.0.tar.gz -C /tmp chatserver-1.0

mkdir -p /tmp/chatclient-1.0
cp -r client/chatclient/* /tmp/chatclient-1.0/
tar czf ~/rpmbuild/SOURCES/chatclient-1.0.tar.gz -C /tmp chatclient-1.0

cp server/chatserver.spec ~/rpmbuild/SPECS/
cp client/chatclient.spec ~/rpmbuild/SPECS/

rpmbuild -ba ~/rpmbuild/SPECS/chatserver.spec
rpmbuild -ba ~/rpmbuild/SPECS/chatclient.spec

RPM_DIR="$HOME/rpmbuild/RPMS/noarch"

sudo dnf -y install "$RPM_DIR/chatserver-1.0-1."*.rpm
sudo dnf -y install "$RPM_DIR/chatclient-1.0-1."*.rpm

echo -e "\n Download complete"
