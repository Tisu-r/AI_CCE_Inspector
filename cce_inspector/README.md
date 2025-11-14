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

- **3-Stage AI Analysis Pipeline**
  1. Asset Identification
  2. Criteria Mapping
  3. Vulnerability Assessment (directly analyzes original config)

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

## Current Status (2025-01-14)

### ✅ Completed
- Core module implementation (AI clients, validators, utilities)
- 3-stage simplified pipeline architecture
- Network plugin with 38 CCE checks
- Multi-AI backend support (Anthropic, OpenAI, Local LLM)
- JSON report generation
- Direct configuration analysis (Stage 3 removed for better accuracy)

### 🧪 Testing Phase
**Current Pipeline:** ✓ 3-Stage Architecture
- Stage 1: Asset Identification (3-5s)
- Stage 2: Criteria Mapping (29-45s, 31-33/38 applicable)
- Stage 3: Vulnerability Assessment (90-100s, direct analysis)

**Test Results:**
- Secure configuration: ✅ 31/31 PASS (100%)
- Vulnerable configuration: ⚠️ AI JSON formatting issues (occasional)

### 🔧 Architecture Improvements
1. **Removed intermediate parsing stage** - Stage 3 (Configuration Parsing) eliminated
2. **Direct analysis approach** - Stage 3 now directly analyzes original config
3. **Improved stability** - Removed unreliable intermediate AI parsing step
4. **Token optimization** - Simplified pipeline reduces complexity

### 📋 TODO: JSON Repair Utility
**Planned Feature:** AI-free JSON post-processor to handle malformed AI responses
- No AI involved - pure Python string processing
- Fix unterminated strings, escaped quotes, bracket matching
- Retry logic with cleaned JSON
- Reduces token costs by fixing issues locally

**See [../docs/DEBUGGING_LOG.md](../docs/DEBUGGING_LOG.md) for detailed debugging history.**

### 📁 Output Files
Results saved to:
```
output/network_{timestamp}_{hostname}.json    # JSON results
output/network_{timestamp}_{hostname}.html    # HTML report
debug/responses/stage4_response_{hostname}.txt # Debug logs
```

### ⚙️ Tested Configuration
- AI Provider: Anthropic Claude (claude-sonnet-4-5-20250929)
- Max Tokens: 8192
- Test Files: Cisco IOS vulnerable/secure configs

## Roadmap

- [x] Network equipment plugin
- [x] Core module implementation
- [x] 4-stage AI pipeline
- [x] Bug fixes (5/5 resolved)
- [ ] Complete Stage 4 testing
- [ ] Device profile implementation
- [ ] Multi-vendor testing (Juniper, Huawei)
- [ ] Unix/Linux plugin
- [ ] Windows plugin
- [ ] Database plugin
- [ ] Application plugin
- [ ] Web UI interface
- [ ] Batch processing mode
- [ ] Integration with SIEM systems
