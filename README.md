# webtainer
a container for manage your website :D

### Requirements
- Ubuntu server with `sudo`
- Python3
- Screen
- Domain that already added `A` record to your public IP _`Note: Disable proxy, for certbot installation. you can enable it after installation done`_

#### Step 1
Download or clone or anything to this repo and put into your `root`.

```
root
┣📂 acontainer
┣📜setup.py
```

#### Step 2
Run this following command
```shell
$ sudo apt update
```
```shell
$ sudo apt install python3
```
```shell
$ sudo apt install python3-pip
```

#### Step 3
Run this
```shell
$ screen -S container
```
```shell
$ python3 setup.py
```
And wait.

---

if you see like this :
```shell
You need to do something :)
Enter username for admin access :
```
just input 
as example I use `webtainer.example.com` for container and `webtainerdb.example.com` for the database domain.
---
if the email input appear, just input your email. it's for certbot installation then a,y,2

if `configuring phpmyadmin` appear. press tab till the red hit `<OK>` and enter.

if this appear :
```shell
All things DONE... Please wait...
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8000
 * Running on http://128.199.138.100:8000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 307-781-813
 ```
 Congratulation! 
 now acces your container domain and login.
 
# Then, How to use it?
---
### Adding domain
make sure you point `A` record to your server IP

Just click `Add Domain` and input.

### Adding website
- Click `Add Website`
- Choose Domain
- Select web type
- App startup file is your main file name. as example `index.html`
- App endpoint is for python. if it's php or html just input file name without extension. example the file is `index.html` then input `index`.
and for python it's
```python
from flask import Flask

app = Flask(__name__)

#App endpoint
application = app
```
- note. the ZIP file is the file that contain webfile. `DON'T ZIP a Folder`
 as example I gave it in example folder. remember, ZIP the entire file in folder, NOT the `example` folder.
- Click add website. (just wait. the process is depending on your file size)
- Then click run
- Just wait...

### Adding database
- Click add database and input database name
- Click ada user to add user
- in the Users tab. you can grant permission for user to some database. just click add user to database and choose database.

### Applying SSL
When SSL status is RED. click instal SSL and wait for status change to `Let's Encrypt`

All done

