import re
import click
import validators
import os
import subprocess

website = dict()
@click.command()
@click.argument('domain')
@click.option('--proxy')
@click.option('--root')
@click.option('--no-ssl', is_flag=True)
def main(domain, proxy, root, no_ssl):
    """Generate a nginx config file"""
   # if os.getuid() != 0:
   #     print("You must be root to run this script")
   #     return 1
    global website
   # if domain:
   #     domain = input("Domain name: ")

    website["ssl"] = not no_ssl
    if not validators.domain(domain):
        print("Domain is not valid")
        return 1
    else:
        website["domain"] = domain
        if not proxy is None and not root is None:
            print("Proxy and root can't mix")
            return 1
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

        
        check()
        write()
        if website["ssl"]:
           certbot() 
        
def write():
    with open("test", 'w') as f:
        f.write("server {\n")
        f.write(f"\tserver_name: {website['domain']};\n")
        f.write(f"\tlisten: 80;\n")
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
    subprocess.run(["certbot","--nginx","-d",domain])
def reloadNginx():
    subprocess.run(["systemctl","reload","nginx"])
def check():
    for element, key in website.items():
        print(f"   {element}: {key}")
    if click.confirm("Are the values correct?"):
        return
    else:
        exit
if __name__ == "__main__":
    main()
