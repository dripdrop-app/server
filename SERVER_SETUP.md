Domain

- Register a domain with Domain Registrar
- Add domain and DNS settings to host platform

Server

- Add ssh key to connect to root account
- Create web server user
- Add a separate ssh key to access web server user
- Set up a firewall with ufw
- Enable OpenSSH on firewall
- Install packages
  - nginx
  - Databases (postgresql, redis, etc.)
- Enable nginx on firewall
- Set up secure account on sql database
- Enable sql database port on firewall
- Add server block to nginx sites-available directory
  - Set root in nginx config to where the built client is
  - Connection upgrade variable
    - ```
            map $http_upgrade $connection_upgrade {
                default upgrade;
                ''      close;
        }
      ```
- Link server block to sites-enabled
- Install certbot to enable ssl with let's encrypt
- Modify nginx configurations to upgrade connection protocols
- Install supervisor to automatically manage processes
- Create supervisor conf file for the server and run supervisord with the web user
