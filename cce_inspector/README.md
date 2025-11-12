# CCE Inspector

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

AI-powered CCE (Common Configuration Enumeration) compliance assessment tool with plugin-based architecture.

## Overview

CCE Inspector automates security compliance checking across multiple asset types using AI (Claude, OpenAI, or local LLM). Based on KISA CCE guidelines for critical information infrastructure.

## Architecture

```
cce_inspector/
├── core/              # Common modules (AI clients, validators, utils)
├── plugins/           # Asset-type specific implementations
│   ├── network/      ✅ IMPLEMENTED
│   ├── unix/         🔜 Planned
│   ├── windows/      🔜 Planned
│   ├── database/     🔜 Planned
│   └── application/  🔜 Planned
└── templates/         # Shared prompt and report templates
```

## Supported Asset Types

### ✅ Network Equipment (Implemented)
- Cisco IOS/IOS-XE, NX-OS, ASA
- Juniper JunOS
- Huawei VRP
- Arista EOS
- HP Comware

### 🔜 Coming Soon
- **Unix/Linux**: RHEL, Ubuntu, Debian, Solaris, AIX
- **Windows**: Server 2012-2022, Active Directory
- **Database**: Oracle, MySQL, PostgreSQL, MS SQL, MongoDB
- **Application**: Apache, Nginx, Tomcat, WebLogic, BIND

## Features

- **4-Stage AI Analysis Pipeline**
  1. Asset Identification
  2. Criteria Mapping
  3. Configuration Parsing
  4. Vulnerability Assessment

- **Multi-AI Backend Support**
  - Anthropic Claude API
  - OpenAI GPT-4
  - Local LLM (Ollama)

- **Dual Output Format**
  - JSON (machine-readable)
  - HTML (professional reports)

- **Plugin Architecture**
  - Easy to add new asset types
  - Isolated implementation per asset type
  - Shared core functionality

## Quick Start

### Installation

```bash
# Clone repository
git clone <repository-url>
cd cce_inspector

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Usage

```bash
# Network equipment compliance check
python main.py --plugin network --config path/to/router_config.cfg

# Specify AI backend
python main.py --plugin network --config router.cfg --ai claude

# Output to specific directory
python main.py --plugin network --config router.cfg --output ./results
```

## Plugin Development

### Adding a New Asset Type

1. Create plugin directory structure:
```
plugins/your_asset/
├── __init__.py
├── config/
│   ├── cce_baseline.json
│   └── profiles.json
├── stages/
│   ├── stage1_asset.py
│   ├── stage2_criteria.py
│   ├── stage3_parsing.py
│   └── stage4_assessment.py
├── samples/
│   └── sample_config.txt
└── README.md
```

2. Implement plugin interface (see `plugins/network/` for reference)

3. Register plugin in main.py

## Configuration

### AI Backend Selection

```env
# .env file
AI_PROVIDER=claude  # or 'openai' or 'local'

# Claude
ANTHROPIC_API_KEY=your_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4

# Local LLM
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3:8b
```

## Project Structure

See [STRUCTURE.md](../network_cce_checker/STRUCTURE.md) for detailed architecture documentation.

## Disclaimer

This tool is based on CCE guidelines published by KISA. Users are responsible for:
- Obtaining official CCE baseline files from KISA
- Ensuring compliance with applicable laws and regulations
- Obtaining customer consent for AI-based analysis

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Submit a pull request

## Roadmap

- [x] Network equipment plugin
- [ ] Unix/Linux plugin
- [ ] Windows plugin
- [ ] Database plugin
- [ ] Application plugin
- [ ] Web UI interface
- [ ] Batch processing mode
- [ ] Integration with SIEM systems
