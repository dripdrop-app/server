- Manual Web Server Setup

- Register a domain with a Domain Registrar

- Digital Ocean Specific

  - For Digital Ocean add custom name servers for DNS settings on domain)
  - Add A records (IPV4) IP resolution records to redirect to droplet

- Set up firewall with ufw

- Enable OpenSSH

- Install necessary packages

- Install and Enable nginx in firewall

- Test by going to domain (nginx test site should show)

- Add new nginx server block to /etc/sites-available/<-project->

- Link server block to sites-enabled

```
packages to install

python3-venv
postgresql
redis
nginx

ufw enable
ufw allow

OpenSSH
Nginx Full

PORT 5000 (TEST)
```
