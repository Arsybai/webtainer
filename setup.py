import os, json
from time import sleep

with open('container/data.json', 'r') as config:
    config = json.load(config)

def clearTerminal():
    try:
        os.system("clear")
    except:
        os.system("cls")

clearTerminal()
print("\nHELLO THERE :)")
sleep(5)
clearTerminal()
print("\nGetting things ready for you...")
sleep(5)
clearTerminal()
print("\nChecking for updates...")
sleep(2)
os.system('sudo rm /usr/lib/python3.11/EXTERNALLY-MANAGED')
os.system('sudo apt update -y')
clearTerminal()
print("\nInstalling requirements...")
sleep(2)
os.system("sudo pip3 install flask")
clearTerminal()
print("\nInstalling requirements...")
sleep(2)
os.system("sudo pip3 install waitress")
os.system("sudo pip3 install psutil")
os.system("sudo pip3 install paramiko")
clearTerminal()

print("\nInstalling Nginx...")
sleep(2)
os.system("sudo apt install nginx -y")
clearTerminal()

print("\nGranting access for Nginx...")
sleep(2)
os.system("sudo ufw allow 'Nginx Full'")
clearTerminal()

print("\nInstalling MySQL Server...")
sleep(2)
os.system("sudo apt install mysql-server -y")
clearTerminal()

print("\nInstalling Php...")
sleep(2)
os.system("sudo apt install php8.1-fpm php-mysql -y")
os.system("mysql -u 'root' -e \"create database flask_panel\"")
os.system("mysql -u 'root' -e \"create user 'fpanel'@'localhost' identified with mysql_native_password by '@Fpanel123'\"")
os.system("mysql -u 'root' -e \"grant all privileges on flask_panel.* to 'fpanel'@'localhost'\"")
clearTerminal()

print("\nInstalling Php...")
sleep(2)
os.system("sudo apt install php-fpm php-mysql -y")
clearTerminal()

print("\nYou need to do something :)")
config['username'] = input("Enter username for admin access : ")
config['password'] = input("Enter password for admin access : ")
container_host = input("Enter container domain : ")
database_host = input("Enter database domain : ")
config['phpmyadmin'] = "https://{}/phpmyadmin".format(database_host)

clearTerminal()
print("Checking....")
sleep(2)
if config['username'] == "":
    print("Installation failed : username can not be empty")
elif config['password'] == "":
    print("Installation failed : password can not be empty")
elif container_host == "":
    print("Installation failed : container domain can not be empty")
elif database_host == "":
    print("Installation failed : database domain can not be empty")
else:
    with open('container/data.json','w') as wconf:
        json.dump(config, wconf, indent=4)
    clearTerminal()
    print('\nBuilding server block...')
    container_block = """server {
    listen 80;
    server_name """+container_host+""";
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}"""
    with open('/etc/nginx/sites-enabled/container', 'w') as ww:
        ww.write(container_block)
    sleep(2)
    clearTerminal()
    print("\nInstalling certbot...")
    sleep(1)
    os.system("sudo apt install certbot python3-certbot-nginx -y")
    clearTerminal()
    print("\nApplying SSL to container...")
    sleep(1)
    os.system("sudo certbot --nginx -d {}".format(container_host))
    clearTerminal()

    print("\nInstalling PhpMyAdmin...")
    sleep(1)
    os.system("sudo apt install phpmyadmin -y")
    os.system("sudo mkdir /var/www/database")
    os.system("sudo chown -R $USER:$USER /var/www/database")
    os.system("sudo ln -s /usr/share/phpmyadmin /var/www/database/phpmyadmin")
    clearTerminal()
    print("\nBuilding server block...")
    tt = """
server {
    listen 80;
    server_name """+database_host+""";
    root /var/www/database;
    index index.html index.htm index.php;
    location / {
        try_files $uri $uri/ =404;
    }
    location ~ \.php$ {
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/var/run/php/php-fpm.sock;
     }
    location ~ /\.ht {
        deny all;
    }
}
"""
    with open('/etc/nginx/sites-available/database', 'w') as ww:
        ww.write(tt)
    os.system("sudo ln -s /etc/nginx/sites-available/database /etc/nginx/sites-enabled/")
    clearTerminal()
    print("\nApplying SSL to database...")
    os.system("sudo certbot --nginx -d {}".format(database_host))
    clearTerminal()
    print("\nRestarting Nginx...")
    os.system("sudo systemctl restart nginx")
    clearTerminal()
    print("\nAll things DONE... Please wait...")
    sleep(5)
    os.system("cd container && python3 app.py")