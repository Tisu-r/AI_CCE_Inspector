# Configuration Files

This directory should contain the baseline configuration files for CCE compliance checking.

## Required Files

Due to copyright considerations with source materials from KISA (Korea Internet & Security Agency), the following files are **not included** in this repository and must be created by users:

### 1. `cce_baseline.json`

Contains the CCE (Common Configuration Enumeration) baseline criteria.

**Required Schema:**

```json
{
  "version": "string",
  "standard": "CCE",
  "updated": "YYYY-MM-DD",
  "description": "string",
  "categories": {
    "category_id": {
      "name": "string (Korean)",
      "name_en": "string (English)",
      "description": "string"
    }
  },
  "checks": [
    {
      "check_id": "string (e.g., N-01)",
      "title": "string (Korean)",
      "title_en": "string (English)",
      "category": "string",
      "severity": "high|medium|low",
      "description": "string",
      "objective": "string",
      "vulnerability": "string",
      "check_patterns": {
        "compliant": ["regex pattern 1", "regex pattern 2"],
        "non_compliant": ["regex pattern 1", "regex pattern 2"]
      },
      "vendor_commands": {
        "cisco": {
          "check": ["command 1", "command 2"],
          "remediation": ["command 1", "command 2"]
        },
        "juniper": {
          "check": ["command 1"],
          "remediation": ["command 1"]
        }
      },
      "evaluation_criteria": {
        "pass_conditions": ["condition 1", "condition 2"],
        "fail_conditions": ["condition 1", "condition 2"]
      }
    }
  ],
  "metadata": {
    "total_checks": 0,
    "severity_distribution": {},
    "category_distribution": {}
  }
}
```

**How to obtain:**
1. Download the official CCE guideline from [KISA](https://www.kisa.or.kr)
2. Extract security check items (N-01, N-02, etc.)
3. Structure them according to the schema above
4. Include regex patterns for configuration matching
5. Add vendor-specific commands (Cisco, Juniper, Huawei, etc.)

---

### 2. `device_profiles.json`

Contains vendor-specific device profiles for configuration parsing.

**Required Schema:**

```json
{
  "version": "string",
  "description": "string",
  "vendors": {
    "vendor_id": {
      "name": "string",
      "description": "string",
      "version_patterns": ["regex pattern 1", "regex pattern 2"],
      "config_markers": {
        "version_line": "regex",
        "hostname_line": "regex",
        "interface_start": "regex"
      },
      "command_syntax": {
        "show_version": "command",
        "show_running": "command",
        "show_interfaces": "command"
      },
      "password_types": {
        "0": "plaintext",
        "5": "MD5 hash",
        "7": "Cisco Type 7"
      },
      "applicable_checks": ["N-01", "N-02", "N-03"]
    }
  },
  "detection_rules": {
    "priority_order": ["vendor_id_1", "vendor_id_2"],
    "detection_method": "version_patterns",
    "fallback": "vendor_id"
  },
  "parsing_hints": {
    "vendor_id": {
      "indentation": "spaces",
      "indent_size": 1,
      "section_hierarchy": false,
      "config_blocks": ["interface", "line", "router"]
    }
  },
  "common_checks": {
    "password_complexity": {
      "min_length": 9,
      "required_character_types": 3
    },
    "session_timeout": {
      "max_recommended_minutes": 10,
      "max_allowed_minutes": 60
    }
  }
}
```

**Supported vendors (examples):**
- `cisco_ios` - Cisco IOS/IOS-XE
- `cisco_nxos` - Cisco NX-OS
- `juniper_junos` - Juniper JunOS
- `huawei_vrp` - Huawei VRP
- `arista_eos` - Arista EOS

---

## Example Minimal Configuration

If you just want to test the tool, create minimal versions:

### Minimal `cce_baseline.json`:

```json
{
  "version": "1.0.0",
  "standard": "CCE",
  "checks": [
    {
      "check_id": "N-01",
      "title": "Password Complexity",
      "severity": "high",
      "check_patterns": {
        "compliant": ["security passwords min-length [9-9][0-9]"],
        "non_compliant": ["security passwords min-length [0-8]"]
      }
    }
  ]
}
```

### Minimal `device_profiles.json`:

```json
{
  "version": "1.0.0",
  "vendors": {
    "cisco_ios": {
      "name": "Cisco IOS",
      "version_patterns": ["Cisco IOS Software"],
      "applicable_checks": ["N-01"]
    }
  }
}
```

---

## Legal Notice

The CCE (Common Configuration Enumeration) standard and guidelines are published by KISA (Korea Internet & Security Agency). Users must obtain these materials from official sources and are responsible for compliance with applicable copyright and licensing terms.

This tool provides the **framework** for automated compliance checking. The **baseline criteria** must be obtained separately.

---

## File Locations

Place the created files in this directory:

```
network_cce_checker/
└── config/
    ├── README.md (this file)
    ├── cce_baseline.json (create this)
    └── device_profiles.json (create this)
```

Both files are listed in `.gitignore` and will not be committed to version control.
