# Application Plugin

## Status: 🔜 Placeholder

This plugin structure is prepared for future implementation of Application software CCE compliance checking.

## Planned Support

### Web Servers
- Apache HTTP Server
- Nginx
- Microsoft IIS

### WAS (Web Application Server)
- Apache Tomcat
- Oracle WebLogic
- Red Hat JBoss
- IBM WebSphere

### DNS
- BIND (Berkeley Internet Name Domain)

### Mail Servers
- Sendmail
- Postfix
- Microsoft Exchange

## Required Files (To be created)

### `config/cce_baseline.json`
- A-01 ~ A-XX: Application CCE check items
- Based on KISA CCE guidelines for application software

### `config/profiles.json`
- Application-specific configuration formats
- Version-specific differences
- Configuration file locations

### `samples/`
- httpd.conf, nginx.conf
- server.xml (Tomcat)
- named.conf (BIND)
- main.cf (Postfix)

## Data Collection Methods

- Configuration file extraction
- Runtime parameter queries
- Module/plugin inventory
- Access control lists

## Contact

Awaiting sample data and requirements to begin implementation.
