# Ubuntu Installation

Install Docker Engine as per Docker's Instructions
https://docs.docker.com/engine/install/ubuntu/

## Add Docker's official GPG key:
```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

## Add the repository to Apt sources:
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```
## Install the Docker packages.
```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
## Login into Docker
```bash
docker login --username <your-username>
```

## Clone the Repository
```bash
git clone https://github.com/jadimabuyu/IPoDWDM-TIG/
```

## Edit the .env file
Change the usernames and passwords, timezone as you please. You can add the routers and their credentials by editing the hosts variable.
Don't forget to change the numberofHosts variable.
```bash
nano .env
```

```bash
INFLUXDB_USERNAME=admin
INFLUXDB_PASSWORD=admin123
INFLUXDB_ORG = yourOrganization
INFLUXDB_BUCKET=yourBucket
INFLUXDB_TOKEN=Cc_ioJXCVPyvQgabo9lVQqPKfD85bI-EQO81cEUD9XT5StYbsnTvnryF5QCemXXpTdiIrJoJXbprLiQcUbbDng==

GRAFANA_USERNAME=admin
GRAFANA_PASSWORD=admin123
GRAFANA_PORT=8080

current_uid=0
timezone=America/Los_Angeles

numberofHosts=2
hosts='[
{"host":"rtme-acx-48l-10.englab.juniper.net","user":"netconf_user","passwd":"PASSWORD"},
{"host":"rtme-mx304-05.englab.juniper.net","user":"netconf_user","passwd":"PASSWORD"},
]'
poolInterval=15
```

## Configure the router
```bash
set system login user netconf_user class super-user
set system services netconf ssh

# If you have the encrypted hash of the password desired
set system login user netconf_user authentication encrypted-password “”
# If you need to type the password in plain text
set system login user netconf_user authentication plain-text-password
```


## Use docker compose to start the containers
```bash
docker compose up -d
```

## Finished
The Grafana Dashboard should be in http://yourIPAddress:yourGrafanaPortNumber
