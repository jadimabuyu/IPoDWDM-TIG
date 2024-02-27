title: Installation

# Installing IPoDWDM-TIG

## Ubuntu 

Install Docker Engine as per Docker's Instructions
https://docs.docker.com/engine/install/ubuntu/

# Add Docker's official GPG key:
```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

# Add the repository to Apt sources:
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
# Install the Docker packages.
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

# Clone the Repository
```bash
git clone https://github.com/jadimabuyu/IPoDWDM-TIG/
```

# Edit the .env file
```bash
git clone https://github.com/jadimabuyu/IPoDWDM-TIG/
```
