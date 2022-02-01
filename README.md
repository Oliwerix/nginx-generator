# nginx-generator
[![Upload Python Package](https://github.com/Oliwerix/nginx-generator/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Oliwerix/nginx-generator/actions/workflows/python-publish.yml)

Command line interface for generating nginx config files

## Features
 - Reverse proxy support
 - Static file support
 - Php support
 - Certbot support

## Usage
    Usage: app.py [OPTIONS] DOMAIN
    
      Generate a nginx config file
    
    Options:
      -p, --proxy TEXT       Proxy address
      -r, --root PATH        Document root
      --php                  Enables php-fpm
      --php-version TEXT     Set php-fpm version
      --filename TEXT        Set config filename (default: domain)
      --no-ssl               Disables automatic certificate using certbot
      --edit                 Open editor after install
      -y, --yes              Do not prompt user
      --dry-run              Writes to temporary file (implies --edit, --no-ssl)
      --ignore-nginx-errors  Don't exit on nginx errors
      --help                 Show this message and exit.

### Examples
    sudo nginx-generator example.com,www.example.com --root /var/www/html
    sudo nginx-generator example.com,www.example.com --proxy http://localhost:8080/
    sudo nginx-generator example.com --root /var/www/html --php --php-version 8.0
## Installation
    sudo pip3 install nginx-generator
### Dependancies
The script is based on python, and is avaliable on PyPI
 - python3.7
 - pip
If you want to get ssl certificates, you need to install `certbot`, and for php you require `php-fpm`
