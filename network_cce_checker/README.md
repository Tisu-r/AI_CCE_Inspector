# Network CCE Inspector

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

AI-powered network device configuration compliance checker based on CCE (Common Configuration Enumeration) standards.

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
