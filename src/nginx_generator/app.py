import re
import click
import validators
import os
import subprocess

website = dict()

@click.command()
@click.argument('domain')
@click.option('--proxy', help="Proxy address")
@click.option('--root', type=click.Path(), help="Document root")
@click.option('--no-ssl', is_flag=True, help="Disables automatic certificate using certbot")
def main(domain, proxy, root, no_ssl):
    """Generate a nginx config file"""
    if os.getuid() != 0:
        print("You must be root to run this script")
        return 1
    global website

    website["ssl"] = not no_ssl
    if not validators.domain(domain):
        print("Domain is not valid")
        return 1
    else:
        website["domain"] = domain
        # if both are set
        if not proxy is None and not root is None:
            print("Proxy and root can't mix")
            return 1
        # if none is set
        if proxy is None and root is None:
            if click.confirm("Use reverse proxy?", default=True):
                website["proxy"] = input("Backend address: ")
            else:
                website["root"] = input("Document root: ")
        
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
        write()
        nginx_reload()
        if website["ssl"]:
           certbot(website["domain"]) 
        
def write():
    """Write to file"""
    filename = f"/etc/nginx/sites-enabled/{website['domain']}"
    if os.path.exists(filename):
        if not click.confirm("File exists! Overwrite?"):
            exit
    with open(filename, 'w') as f:
        f.write("server {\n")
        f.write(f"\tserver_name {website['domain']};\n")
        f.write(f"\tlisten 80;\n")
        if "proxy" in website:
            f.write("\tlocation / {\n");
            f.write(f"\t\tproxy_pass {website['proxy']};\n")
            with open("proxy_settings") as proxySettings:
                for line in proxySettings:
                    f.write(line)
            f.write("\t}")
        if "root" in website:
            f.write(f"\troot: {website['root']};\n")
        f.write("}\n")

def certbot(domain):
    """Runs certbot for specified domain"""
    subprocess.run(["certbot","--nginx","-d",domain])
def nginx_reload():
    """Reloads nginx"""
    subprocess.run(["systemctl","reload","nginx"])
def check():
    """Display settings and query user"""
    for element, key in website.items():
        print(f"   {element}: {key}")
    return click.confirm("Are the values correct?")
if __name__ == "__main__":
    main()
