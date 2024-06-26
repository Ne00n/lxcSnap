server {
    listen 80;
    server_name master.mahstorage.com;

    location / {
        auth_basic "Restricted Access";
        auth_basic_user_file /etc/nginx/.htpasswd;
        proxy_pass http://127.0.0.1:9333;
        proxy_set_header Host $host;
    }
}