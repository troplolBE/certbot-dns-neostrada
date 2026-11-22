# certbot-dns-neostrada

Neostrada DNS Authenticator plugin for Certbot

This plugin automates the process of completing a `dns-01` challenge by creating, and subsequently removing, a TXT record using the Neostrada API.

## Configuration
Go to your account and in the setting click on API keys. Once you have acquired an API key, you need to put them in a `.ini` file and give it to Certbot by making use of the `--certbot_dns_neostrada:dns-neostrada-credentials` argument.

The ini file should look like this:
```text
# Neostrada API key used by Certbot
dns_neostrada_api_key=api-key
```

## Installation
```shell
pip install certbot-dns-neostrada
```

## Testing and development
Clone the repository and install the package in edit mode.
```shell
git clone https://github.com/troplolBE/certbot-dns-neostrada.git
python3 -m venv env
pip install -e .
```

Now, check that the plugin is discovered by Certbot with the plugins comamnd.
```shell
certbot plugins
```

Once you have done your changes or if you just want to test the plugin, create the `.ini` file like explained earlier and issue the following command.
```shell
certbot certonly --staging --authenticator dns-neostrada --dns-neostrada-credentials creds.ini --dns-neostrada-propagation-seconds 60 -d <domain> --config-dir ./tmp/config --work-dir ./tmp/work --logs-dir ./tmp/logs --agree-tos -m <email> --non-interactive
```

Make sure to replace `<domain>` with a domain that you own in Neostrada and `<email>` with your own e-mail address.