#!/bin/bash

if [ ! -d /opt/miro_browser ]; then
	mkdir /opt/miro_browser;
fi

cp -r browser/* /opt/miro_browser
chown -R miro:miro /opt/miro_browser

cp browser/conf/miro_browser.service /etc/systemd/system;
systemctl start miro_browser.service;
systemctl enable miro_browser.service;
