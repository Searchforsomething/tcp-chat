# Консольный TCP-чат

Чат состоит из многопоточного сервера и клиента.

## Установка

Клонируем репозиторий

```bash
git clone https://github.com/Searchforsomething/tcp-chat.git
```

Сервер и клиент устанавливаются через RPM, поэтому для начала надо установить инструменты:

```bash
sudo dnf update
sudo dnf install rpm-build rpmdevtools
```

Далее создаём структуру

```bash
rpmdev-setuptree
```

Получаем структуру вроде

```
~/rpmbuild/
├── BUILD
├── RPMS
├── SOURCES
├── SPECS
└── SRPMS
```

Упаковываем `chatclient` и `chatserver` в архивы и помещаем их в `SOURCES`

```bash
tar czf ~/rpmbuild/SOURCES/chatserver-1.0.tar.gz server/chatserver/
tar czf ~/rpmbuild/SOURCES/chatclient-1.0.tar.gz client/chatclient/
```

Копируем `.spec` файлы в `SPECS`

```bash
cp server/chatserver.spec ~/rpmbuild/SPECS
cp client/chatclient.spec ~/rpmbuild/SPECS
```

Собираем RPM

```bash
rpmbuild -ba ~/rpmbuild/SPECS/chatserver.spec
rpmbuild -ba ~/rpmbuild/SPECS/chatclient.spec
```

Готовые `.rpm` появятся в:

```
~/rpmbuild/RPMS/noarch/chatserver-1.0-1.el8.noarch.rpm
~/rpmbuild/RPMS/noarch/chatclient-1.0-1.el8.noarch.rpm
```

Установка:

```bash
sudo dnf install ~/rpmbuild/RPMS/noarch/chatserver-1.0-1.el8.noarch.rpm
sudo dnf install ~/rpmbuild/RPMS/noarch/chatсlient-1.0-1.el8.noarch.rpm
```

## Инструкция по работе с сервером

Сервер работает как systemd сервис, чтобы его запустить надо выполнить:

```bash
sudo systemctl start chatserver
```

Следовательно, для его остановки:

```bash
sudo systemctl stop chatserver
```

## Инструкция по работе с клиентом

Запуск: 

```bash
chatclient
```

После запуска программа предложит выбрать имя пользователя, оно должно быть уникальным. В случае наличия дубликата
программа выведет сообщение об этом и предложит выбрать другое имя. Сообщения отправляются в формате:
```
username: message
```

Работа клиента завершается нажатием ^C

## Ограничения и недостатки

В связи с ограниченным временем на реализацию у кода есть некоторые недостатки

1. В коде используются глобальные переменные, что неудобно для расширяемости и тестируемости.
2. Весь код сервера лежит в 1 файле, и весь код клиента тоже. Такой подход делает код менее читаемым и более громоздким.
3. (bonus) Изначально не планировалось, что сервер будет работать как сервис, поэтому в коде есть обработка SIGINT,
которая в итоге не пригодилась