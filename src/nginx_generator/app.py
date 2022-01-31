import re
import click
import validators
import os
import subprocess

config = {
    "php-fpm": "7.4",
    "nginx-blocks": "/etc/nginx/sites-enabled/"
        }
website = dict()

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

@click.command()
@click.argument('domain')
@click.option('--proxy', help="Proxy address")
@click.option('--root', type=click.Path(), help="Document root")
@click.option('--php', is_flag=True, help="Enables php-fpm")
@click.option('--php-version', help=f"Set php-fpm version", default=config['php-fpm'])
@click.option('--no-ssl', is_flag=True, help="Disables automatic certificate using certbot")
@click.option('--edit', is_flag=True, help="Open editor after install")
@click.option('--yes', '-Y', is_flag=True)
@click.option('--dry-run', is_flag=True, help="Writes to temporary file (implies --edit, --no-ssl)")
def main(domain, proxy, root, php, php_version, no_ssl, edit, yes, dry_run):
    """Generate a nginx config file"""
    globals()['yes'] = yes
    globals()['dry_run'] = dry_run
    global website
    if php:
        website["php"] = php
        website["php-version"] = php_version

    if dry_run:
        edit = True
        no_ssl = True
    domains = domain.split(",")
    domain = domains[0]
    if os.getuid() != 0:
        print("You must be root to run this script")
        return 1

    website["ssl"] = not no_ssl
    checkDomains(domains)
    website["domain"] = domain
    website["domains"] = domains
    # if both are set
    if not proxy is None and not root is None:
        print("Proxy and root can't mix")
        return 1
    # if none is set
    if proxy is None and root is None:
        if confirm("Use reverse proxy?", default=True):
            website["proxy"] = click.prompt("Backend address: ")
        else:
            website["root"] = click.prompt("Document root: ", type=click.Path())
    
    if not proxy is None:
        website["proxy"] = proxy
    if not root is None:
        website["root"] = root


    if "proxy" in website:
        if not validators.url(website["proxy"]):
            print("Proxy url not valid")
            return 1 

    if not check():
        return 1

    if dry_run:
        filename = f"/tmp/{website['domain']}"
    else:
        filename = config['nginx-blocks']+website['domain']


    print(f"Writing config to {filename}")
    write(filename)
    nginx_reload()
    if website["ssl"]:
       certbot(website["domains"]) 
    if edit:
        print("a")
        editConfig(filename)
        
def checkDomains(domains):
    """Verify domains"""
    for domain in domains:
        if not validators.domain(domain):
            print(f"domain {domain} is not valid!")
            exit()
def write(filename):
    """Write to file"""
    if os.path.exists(filename):
        if not confirm("File exists! Overwrite?"):
            return 0
    with open(filename, 'w') as f:
        def copyFile(filename):
            with open(filename) as cp:
                for line in cp:
                    f.write(line)

        copyFile("snippets/about")
        f.write("server {\n")
        f.write(f"\tserver_name {' '.join(website['domains'])};\n")
        f.write(f"\tlisten 80;\n")
        if "proxy" in website:
            f.write("\tlocation / {\n");
            f.write(f"\t\tproxy_pass {website['proxy']};\n")
            copyFile("snippets/proxy_settings")
            f.write("\t}")
        if "php" in website:
            f.write("\tlocation ~* \.php$ {\n")
            f.write(f"\t\tfastcgi_pass unix:/run/php/php{website['php-version']}-fpm.sock;\n")
            copyFile("snippets/php-fpm")
            f.write("\t}\n")
            f.write("\tindex index.php index.html;\n")
        if "root" in website:
            f.write(f"\troot {website['root']};\n")
        f.write("}\n")

def certbot(domains):
    print(f"Starting certbot for domains {' '.join(domains)}")
    """Runs certbot for specified domain"""
    subprocess.run(["certbot","--nginx","-d",','.join(domains)])
def nginx_reload():
    """Reloads nginx"""
    subprocess.run(["systemctl","reload","nginx"])
def nginx_test():
    """Nginx test config"""
    subprocess.run(["nginx", "-t"])
def editConfig(filename):
    EDITOR = os.environ.get('EDITOR' 'vim')
    if EDITOR is None:
        EDITOR = "vim"
    subprocess.call([EDITOR, filename])
    nginx_test()
def confirm(prompt, default=False):
    if not yes:
        return click.confirm(prompt, default)
    return True
def check():
    """Display settings and query user"""
    for element, key in website.items():
        print(f"   {element}: {key}")
    return confirm("Are the values correct?")
if __name__ == "__main__":
    main()
