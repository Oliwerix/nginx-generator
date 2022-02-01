# nginx-generator
[![Upload Python Package](https://github.com/Oliwerix/nginx-generator/actions/workflows/python-publish.yml/badge.svg)](https://github.com/Oliwerix/nginx-generator/actions/workflows/python-publish.yml)

## Features
 - Reverse **proxy** support
 - Static file support
 - **PHP** support
 - **Certbot** support
 - Syntax checking

# Description
**nginx-generator** is a command-line program for generating nginx config files. It requires python 3.7+. nginx-generator can generate nginx-config files, aquire ssl certificates using **certbot**, enable php and much more. It is tested on Ubutnu server 20.04

    nginx-generator [OPTIONS] DOMAIN

# Options
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

# Examples
Serve a static site on `example.com` and `www.example.com` with the static files located at `/var/www/html`, you will get an SSL certificate automatically.

    sudo nginx-generator example.com,www.example.com --root /var/www/html

Proxy a backend on `http://localhost:8080`

    sudo nginx-generator example.com,www.example.com --proxy http://localhost:8080/

Serve a php website with `php8.0`

    sudo nginx-generator example.com --root /var/www/html --php --php-version 8.0

Don't get SSL and open an editor after file creation
    
    sudo nginx-generator example.com --no-ssl --edit

# Installation
nginx-generator can be installed using [pip](https://pip.pypa.io/)
    sudo pip3 install nginx-generator
### Requirements
The script is based on python, and is avaliable on PyPI
 - [python](https://www.python.org/) (>=3.7)
 - pip
### Optional
 - [certbot](https://certbot.eff.org/) (for autoamtic SSL certificates)
 - php with php-fpm (for php support)
