# nginx-generator
[![Upload Python Package](https://github.com/Oliwerix/nginx-generator/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Oliwerix/nginx-generator/actions/workflows/python-publish.yml)
Command line interface for generating nginx config files

## Features
 - Reverse proxy support
 - Static file support
 - Php support
 - Certbot support

## Usage
    Usage: nginx-generator [OPTIONS] DOMAIN

      Generate a nginx config file

    Options:
      --proxy TEXT        Proxy address
      --root PATH         Document root
      --php               Enables php-fpm
      --php-version TEXT  Set php-fpm version
      --no-ssl            Disables automatic certificate using certbot
      --edit              Open editor after install
      -Y, --yes
      --dry-run           Writes to temporary file (implies --edit, --no-ssl)
      --help              Show this message and exit.
### Examples
    nginx-generator example.com,www.example.com --root /var/www/html
    nginx-generator example.com,www.example.com --proxy http://localhost:8080/
    nginx-generator example.com --root /var/www/html --php --php-version 8.0
## Installation
    pip3 install nginx-generator
If you want to get ssl certificates, you need to install `certbot`, and for php you require `php-fpm`
