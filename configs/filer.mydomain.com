server {
    listen 80;
    server_name filer.mahstorage.com;
    client_max_body_size 100G;

    location / {
        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
    }
}