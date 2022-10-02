Domain

- Register a domain with Domain Registrar
- Add domain and DNS settings to host platform

Server

- Create a new user for builds
- Add SSH Keys to authorized_keys file for user accounts
- Set up a firewall with ufw
- Enable OpenSSH on firewall
- Install packages
  - nginx
  - docker
- Enable nginx on firewall
- Add server block to nginx sites-available directory
- Link server block to sites-enabled
- Install certbot to enable ssl with let's encrypt
- Modify nginx configurations to upgrade connection protocols
