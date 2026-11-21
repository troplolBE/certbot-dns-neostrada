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