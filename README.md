# NEW THINGS TO ADD

- Get YT Collections working with music

  - Create worker that pulls videos everyday from subscribed channels (keep last 30 days)
  - Maybe set reminder to self if last seen is 10 days for yt collections

- Manual Web Server Setup

- Create user account [https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-20-04]

- Register a domain with a Domain Registrar

- Digital Ocean Specific

  - For Digital Ocean add custom name servers for DNS settings on domain)
  - Add A records (IPV4) IP resolution records to redirect to droplet

- Set up firewall with ufw

- Enable OpenSSH

- Install necessary packages

- Install and Enable nginx in firewall

- Test by going to domain (nginx test site should show)

- Add new nginx server block to /etc/sites-available/<-project-> [https://www.digitalocean.com/community/tutorials/how-to-install-nginx-on-ubuntu-20-04]

- Link server block to sites-enabled

- Set up server and check it out

- SSL, install certbot [https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-20-04]

- Add upgrade protocols for http and connection [https://futurestud.io/tutorials/nginx-how-to-fix-unknown-connection_upgrade-variable]

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

TO DO

- Move Youtube Links to separate component files
- Add iframe youtube videos to play on site
- Use a new button to go navigate to content on youtube
