Name:           chatclient
Version:        1.0
Release:        1%{?dist}
Summary:        Simple Python chat client

License:        MIT
URL:            https://github.com/Searchforsomething/tcp-chat
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       python3

%description
A lightweight Python chat client.

%prep
%setup -q

%build

%install

mkdir -p %{buildroot}/usr/libexec/chatclient
cp client.py %{buildroot}/usr/libexec/chatclient/


mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/chatclient << EOF
#!/bin/bash
exec /usr/bin/python3 /usr/libexec/chatclient/client.py "\$@"
EOF
chmod +x %{buildroot}/usr/bin/chatclient

%files
%license LICENSE
%doc README.md
/usr/libexec/chatclient/client.py
/usr/bin/chatclient

%changelog
* Tue May 06 2025 Anastasia Korotykina <me@example.com> - 1.0-1
- Initial package of chatclient
