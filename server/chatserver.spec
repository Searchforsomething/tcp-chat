Name:           chatserver
Version:        1.0
Release:        1%{?dist}
Summary:        Simple Python chat server

License:        MIT
URL:            https://github.com/Searchforsomething/tcp-chat
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3

%description
A lightweight Python chat server.

%prep
%setup -q

%build


%install
mkdir -p %{buildroot}/usr/libexec/chatserver
mkdir -p %{buildroot}/usr/lib/systemd/system
mkdir -p %{buildroot}/var/log/chatserver

cp server.py %{buildroot}/usr/libexec/chatserver/

cat > %{buildroot}/usr/lib/systemd/system/chatserver.service << EOF
[Unit]
Description=Chat Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /usr/libexec/chatserver/server.py
WorkingDirectory=/usr/libexec/chatserver
Restart=on-failure
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

%files
%license LICENSE
%doc README.md
/usr/libexec/chatserver/server.py
/usr/lib/systemd/system/chatserver.service

%dir /var/log/chatserver

%post
touch /var/log/chatserver/server.log
chown root:root /var/log/chatserver/server.log
chmod 644 /var/log/chatserver/server.log
systemctl daemon-reexec
systemctl enable chatserver.service > /dev/null || :

%preun
if [ $1 -eq 0 ]; then
    systemctl --no-reload disable chatserver.service > /dev/null || :
    systemctl stop chatserver.service > /dev/null || :
fi

%postun
systemctl daemon-reexec