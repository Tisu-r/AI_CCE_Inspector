# Windows Server Plugin

## Status: 🔜 Placeholder

This plugin structure is prepared for future implementation of Windows Server CCE compliance checking.

## Planned Support

- Windows Server 2012 / 2016 / 2019 / 2022
- Active Directory Domain Services
- IIS (Internet Information Services)

## Required Files (To be created)

### `config/cce_baseline.json`
- W-01 ~ W-XX: Windows CCE check items
- Based on KISA CCE guidelines for Windows systems

### `config/profiles.json`
- Windows-specific configuration locations
- Registry keys, Group Policy settings
- PowerShell commands

### `samples/`
- Sample configuration exports
- Secure vs vulnerable examples

## Data Collection Methods

- Registry exports
- Group Policy results (gpresult)
- Security policy (secedit /export)
- PowerShell Get-* cmdlets

## Contact

Awaiting sample data and requirements to begin implementation.
