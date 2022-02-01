import re
import click
import validators
import os
import subprocess

config = {
    "php-fpm": "7.4",
    "nginx-blocks": "/etc/nginx/sites-enabled/"
        }
# The one variable to rule them all
website = dict()

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

@click.command()
@click.argument('domain')
@click.option('--proxy', '-p', help="Proxy address")
@click.option('--root', '-r', type=click.Path(), help="Document root")
@click.option('--php', is_flag=True, help="Enables php-fpm")
@click.option('--php-version', help=f"Set php-fpm version", default=config['php-fpm'])
@click.option('--filename', help="Set config filename (default: domain)")
@click.option('--no-ssl', is_flag=True, help="Disables automatic certificate using certbot")
@click.option('--edit', is_flag=True, help="Open editor after install")
@click.option('--yes', '-y', is_flag=True, help="Do not prompt user")
@click.option('--dry-run', is_flag=True, help="Writes to temporary file (implies --edit, --no-ssl)")
@click.option('--ignore-nginx-errors', is_flag=True, help="Don't exit on nginx errors")
@click.option('-v',is_flag=True, help="Verbose")
def main(domain, proxy, root, php, php_version,filename, no_ssl, edit, yes, dry_run, ignore_nginx_errors, v):
    """Generate a nginx config file"""
    if os.getuid() != 0:
        click.echo("You must be root to run this script")
        return 1
    if(ignore_nginx_errors):
        click.secho("Warning: ignoring nginx errors", fg="yellow")
    nginx_test(_exit=not ignore_nginx_errors)
    
    globals()['yes'] = yes
    globals()['dry_run'] = dry_run
    globals()['verbose'] = v
    global website
    if php:
        website["php"] = php
        website["php-version"] = php_version

    if dry_run:
        edit = True
        no_ssl = True
    domains = domain.split(",")
    domain = domains[0]


    website["ssl"] = not no_ssl
    checkDomains(domains)

    
    website["domain"] = domain
    website["domains"] = domains
    website["filename"] = domain if filename is None else filename
    # if both are set
    if not proxy is None and not root is None:
        click.echo("Proxy and root can't mix")
        return 1
    # if none is set
    if proxy is None and root is None:
        if confirm("Use reverse proxy?", default=True):
            website["proxy"] = click.prompt("Proxy backend address")
        else:
            # Click ignores type for some reason 
            #website["root"] = click.prompt("Document root", type=click.Path(file_okay=False))
            website["root"] = click.prompt("Document root")
    # This needs to be like this because the check will fail 
    if not proxy is None:
        website["proxy"] = proxy
    if not root is None:
        website["root"] = root


    if "proxy" in website:
        if not validators.url(website["proxy"]):
            click.echo("Proxy url not valid")
            return 1 

    check()
    if dry_run:
        filename = f"/tmp/{website['filename']}"
    else:
        filename = config['nginx-blocks']+website['filename']


    click.echo(f"Writing config to {filename}")
    write(filename)
    if nginx_test():
        nginx_reload()
    else:
        click.secho("Warning: nginx not reloaded!", fg="yellow")
    if website["ssl"]:
        certbot(website["domains"]) 
    if edit:
        editConfig(filename)
    nginx_reload()
    click.secho(f"Generated config is at {filename}", fg='green')
        
def checkDomains(domains):
    """Verify domains"""
    for domain in domains:
        if not validators.domain(domain):
            click.echo(f"domain {domain} is not valid!")
            exit()
def write(filename):
    """Write to file"""
    if os.path.exists(filename):
        if not confirm(click.style("File exists! Overwrite?", fg='red')):
            return 0
    with open(filename, 'w') as f:
        def copyFile(filename):
            """copy contens of input filename to output file `f`"""
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
    click.echo(f"Starting certbot for domains {' '.join(domains)}")
    """Runs certbot for specified domain"""
    command = ["certbot", "-d" , ','.join(domains), "--nginx", '-n' if yes else None]
    command = list(filter(None, command))
    if verbose:
        click.echo(subprocess.list2cmdline(command))
    subprocess.run(command)
def nginx_reload():
    """Reloads nginx"""
    subprocess.run(["systemctl","reload","nginx"])
    click.secho("Reloaded nginx", fg="green")
def nginx_test(alert=True, _exit=False):
    """Nginx test config, returns True if OK"""
    try:
        subprocess.run(["nginx", "-t"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        if alert:
            click.secho("Error in your nginx configuration:", fg="red")
            subprocess.run(["nginx", "-T"])
        if _exit:
            exit()
        return False
    else:
        return True
def editConfig(filename):
    """Open editor"""
    def editFile(filename):
        EDITOR = os.environ.get('EDITOR')
        if EDITOR is None:
            EDITOR = "vim"
        subprocess.call([EDITOR, filename])

    editFile(filename)
    while not nginx_test():
        # this is more or less like a do while loop
        confirm("Want to edit the file again?", abort=True, default=True, ignore_yes=True)
        editFile(filename)

def confirm(prompt, default=False, abort=False, ignore_yes=False):
    if not yes or ignore_yes:
        return click.confirm(prompt, default, abort)
    return True
def check():
    """Display settings and query user"""
    if not yes:
        click.secho("Please verify!", fg='yellow')
    for key, element in website.items():
        # Omit lists shorter than one element
        if type(element) is list:
            if len(element) > 1:
                click.echo(f"   {key}: {', '.join(element)}")
        else:
            click.echo(f"   {key}: {element}")
    confirm("Are the values correct?", abort=True)
if __name__ == "__main__":
    main()
