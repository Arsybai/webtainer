def html(site_):
    block_ = """
server {
    listen 80;
    server_name """+site_['url']+""";
    root """+site_['path']+""";
    index """+site_['filename']+""";
    location / {
        try_files $uri $uri/ =404;
    }
    location ~ /\.ht {
        deny all;
    }
}"""
    return block_

def php(site_):
    block_ = """
server {
    listen 80;
    server_name """+site_['url']+""";
    root """+site_['path']+""";
    index """+site_['filename']+""";
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
}"""
    return block_

def python(site_):
    block_ = """
server {
    listen 80;
    server_name """+site_['url']+""";
    location / {
        proxy_pass http://127.0.0.1:"""+site_['port']+""";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}"""
    return block_