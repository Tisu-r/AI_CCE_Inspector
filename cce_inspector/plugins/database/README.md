# Database Plugin

## Status: 🔜 Placeholder

This plugin structure is prepared for future implementation of Database CCE compliance checking.

## Planned Support

- **Oracle Database**: 11g, 12c, 19c, 21c
- **MySQL / MariaDB**: 5.7, 8.0
- **PostgreSQL**: 12+
- **MS SQL Server**: 2016, 2019, 2022
- **MongoDB**: 4.x, 5.x

## Required Files (To be created)

### `config/cce_baseline.json`
- DB-01 ~ DB-XX: Database CCE check items
- Based on KISA CCE guidelines for DBMS

### `config/profiles.json`
- DBMS-specific configuration parameters
- SQL queries for security assessment
- Initialization parameter checks

### `samples/`
- Sample configuration dumps
- Parameter files (init.ora, my.cnf, postgresql.conf)
- Security audit results

## Data Collection Methods

- SQL queries for configuration parameters
- Configuration file dumps
- User/privilege information
- Audit log settings

## Contact

Awaiting sample data and requirements to begin implementation.
