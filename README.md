# 2021_IoT_Challenge

/etc/systemd/system/IoT.service
```
[Unit]
Description = IoT Service.
After = network.target

[Service]
User = root
Group = nginx
WorkingDirectory = /usr/share/nginx/iot
Environment = "PATH=/usr/share/nginx/iot/flask/bin"
ExecStart = /usr/share/nginx/iot/flask/bin/gunicorn -b unix:iot.sock -k eventlet -w 1 app:app

[Install]
WantedBy = multi-user.target
```

/etc/nginx/nginx.conf
```
# Default server configuration
server {
    server_name $domain;

    location / {
        include proxy_params;
        proxy_pass http://unix:/usr/share/nginx/iot/iot.sock;
        proxy_http_version 1.1;
        # proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "Upgrade";
    }

    location /socket.io/ {
        include proxy_params;
        proxy_http_version 1.1;
        proxy_buffering off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_pass http://unix:/usr/share/nginx/iot/iot.sock/socket.io/;
    }
    
    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/$domain/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/$domain/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
}

server {
    if ($host = $domain]) {
        return 301 https://$host$request_uri;
    } # managed by Certbot
    
    listen 80 ;
    listen [::]:80 ;
    
    server_name $domain; # managed by Certbot
    return 404; # managed by Certbot
}
```
