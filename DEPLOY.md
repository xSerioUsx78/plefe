# Install dependencies

apt install git nginx apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

apt update -y

apt-cache policy docker-ce

apt install docker-ce

# Configuring nginx

unlink /etc/nginx/sites-enabled/default

cp ./nginx/plefe /etc/nginx/sites-available/
ln -s /etc/nginx/sites-available/plefe /etc/nginx/sites-enabled/
systemctl restart nginx

# Build and running the images

docker compose up -d
