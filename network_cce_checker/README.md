# Network CCE Inspector

[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

AI-powered network device configuration compliance checker based on CCE (Common Configuration Enumeration) standards.

> **이 프로그램은 크리에이티브 커먼즈 저작자표시-비영리-동일조건변경허락 4.0 국제 라이선스에 따라 이용할 수 있습니다.**
>
> **This work is licensed under a Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.**

## Features

- **Multi-stage AI Analysis**: Asset identification, criteria mapping, configuration parsing, and vulnerability assessment
- **Flexible AI Backend**: Support for OpenAI, Anthropic Claude, or local LLM (Ollama)
- **Structured Output**: JSON-based results with comprehensive HTML reports
- **Extensible Architecture**: Easy to add new compliance standards and device types
- **Smart Caching**: Reduces API costs by caching criteria mappings

## Directory Structure

```
network_cce_checker/
├── main.py                     # Main entry point
├── config.py                   # Configuration management
├── validators.py               # Response validation logic
│
├── ai_clients/                 # AI client implementations
│   ├── __init__.py
│   ├── base.py                # Abstract base client
│   ├── openai_client.py       # OpenAI integration
│   ├── anthropic_client.py    # Anthropic Claude integration
│   └── local_llm_client.py    # Local LLM (Ollama) integration
│
├── stages/                     # Assessment stages
│   ├── __init__.py
│   ├── asset_identification.py
│   ├── criteria_mapping.py
│   ├── config_parsing.py
│   └── vulnerability_assessment.py
│
├── utils/                      # Utilities
│   ├── __init__.py
│   ├── logger.py              # Logging system
│   ├── file_handler.py        # File operations
│   ├── json_parser.py         # JSON extraction from AI responses
│   └── cache.py               # Caching system
│
├── templates/                  # Templates
│   ├── prompts/               # AI prompt templates
│   │   ├── stage1_asset_identification.txt
│   │   ├── stage2_criteria_mapping.txt
│   │   ├── stage3_config_parsing.txt
│   │   └── stage4_vulnerability_assessment.txt
│   └── reports/               # Report templates
│       ├── html_report.jinja2
│       └── styles.css
│
├── config/                     # Configuration files
│   ├── cce_baseline.json      # CCE baseline definitions
│   └── device_profiles.json   # Device-specific profiles
│
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_stages.py
│   └── test_integration.py
│
├── data/                       # Data directory
│   ├── sample_configs/        # Sample configuration files
│   ├── outputs/               # Assessment results
│   └── cache/                 # Cached criteria mappings
│
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd network_cce_checker
```

2. **Important: Prepare baseline files**

   Due to copyright considerations, the CCE baseline files are not included in this repository. You need to:

   - Obtain the official CCE guideline from [KISA (Korea Internet & Security Agency)](https://www.kisa.or.kr)
   - Create `config/cce_baseline.json` based on the CCE standards
   - Create `config/device_profiles.json` for vendor-specific configurations

   See `config/README.md` for the required JSON schema.

3. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys and preferences
```

## Configuration

### Using API-based LLMs (OpenAI or Anthropic)

Edit `.env`:
```env
AI_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

### Using Local LLM (Ollama)

1. Install Ollama: https://ollama.ai
2. Pull a model:
```bash
ollama pull llama3:8b
```

3. Edit `.env`:
```env
AI_PROVIDER=local
LOCAL_LLM_URL=http://localhost:11434
LOCAL_LLM_MODEL=llama3:8b
```

## Usage

### Basic Usage

```bash
python main.py --config path/to/device_config.cfg
```

### Advanced Options

```bash
# Specify output directory
python main.py --config device.cfg --output ./results

# Disable caching
python main.py --config device.cfg --no-cache

# Use specific AI provider
python main.py --config device.cfg --provider openai

# Batch processing
python main.py --directory ./configs/ --batch
```

### Python API

```python
from main import CCEChecker
from config import Config
from ai_clients import get_client

# Load configuration
config = Config.from_env()

# Initialize AI client
ai_client = get_client(config.ai_provider, config)

# Create checker
checker = CCEChecker(ai_client, config)

# Run assessment
result = checker.run_assessment("path/to/config.cfg")

# Access results
print(f"Compliance Score: {result['summary']['compliance_score']}%")
print(f"Failed Checks: {result['summary']['failed']}")
```

## Output

The tool generates two types of output:

1. **JSON Report**: Machine-readable structured data
   - Location: `data/outputs/result_<timestamp>.json`

2. **HTML Report**: Human-readable detailed report
   - Location: `data/outputs/report_<timestamp>.html`
   - Includes: Executive summary, asset info, findings, recommendations

## Supported Devices

Currently supported network devices:
- Cisco IOS/IOS-XE
- Cisco NX-OS
- Cisco ASA
- Juniper JunOS
- Huawei VRP

## Compliance Standards

- **CCE** (Common Configuration Enumeration) - Default
- Future: CIS Benchmarks, DISA STIG, PCI DSS

## Development

### Running Tests

```bash
# All tests
pytest

# With coverage
pytest --cov=network_cce_checker

# Specific test
pytest tests/test_validators.py
```

### Code Quality

```bash
# Format code
black .

# Linting
flake8 .

# Type checking
mypy .
```

## Contributing

This project is developed for public benefit. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

### 라이선스 (한국어)

이 프로그램은 **크리에이티브 커먼즈 저작자표시-비영리-동일조건변경허락 4.0 국제 라이선스**(CC BY-NC-SA 4.0)에 따라 이용할 수 있습니다.

**허용 사항:**
- ✅ 학습 및 교육 목적의 사용
- ✅ 개인적, 비상업적 용도로 자유롭게 사용
- ✅ 코드 수정 및 재배포 (동일 라이선스 적용 시)
- ✅ 보안 연구 및 분석

**금지 사항:**
- ❌ 상업적 이용 (컨설팅, 유료 서비스 등)
- ❌ 원저작자 표시 없이 사용
- ❌ 다른 라이선스로 재배포

자세한 내용은 [LICENSE](../LICENSE) 파일 또는 https://creativecommons.org/licenses/by-nc-sa/4.0/deed.ko 를 참조하세요.

---

### License (English)

This work is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License** (CC BY-NC-SA 4.0).

**You are free to:**
- ✅ Use for learning and educational purposes
- ✅ Use for personal, non-commercial purposes
- ✅ Modify and redistribute (under the same license)
- ✅ Use for security research and analysis

**You are NOT allowed to:**
- ❌ Use for commercial purposes (consulting, paid services, etc.)
- ❌ Use without proper attribution
- ❌ Redistribute under a different license

For full details, see the [LICENSE](../LICENSE) file or visit https://creativecommons.org/licenses/by-nc-sa/4.0/

## Disclaimer

This tool is based on CCE (Common Configuration Enumeration) guidelines published by KISA (Korea Internet & Security Agency). The baseline criteria are derived from publicly available security standards.

**Note:** Users are responsible for ensuring compliance with applicable laws and regulations when using this tool.

## Support

For issues and questions:
- GitHub Issues: <repository-url>/issues
- Documentation: <repository-url>/wiki

## Roadmap

- [ ] Web UI interface
- [ ] More compliance standards (CIS, STIG)
- [ ] Auto-remediation suggestions
- [ ] Continuous monitoring mode
- [ ] Multi-vendor support expansion
- [ ] Integration with SIEM systems

## Acknowledgments

Based on NIST CCE standards and network security best practices.
