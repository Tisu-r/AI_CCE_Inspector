"""Quick test to see Claude's actual response for Stage 1"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cce_inspector.core.ai_clients import create_ai_client
from cce_inspector.core.utils import FileHandler

# Load config
config_file = project_root / "cce_inspector/plugins/network/samples/cisco_ios_vulnerable.cfg"
config_text = FileHandler.read_text(config_file)

# Load template
template_file = project_root / "cce_inspector/templates/prompts/stage1_asset_identification.txt"
template = FileHandler.read_text(template_file)

# Build prompt
prompt = template.replace("{{CONFIGURATION}}", config_text[:500])  # Just first 500 chars

# Create client
client = create_ai_client()

# Get response
print("Sending request to Claude...")
response = client.generate(
    prompt=prompt,
    system_prompt="You are a network security expert analyzing device configurations."
)

print("\n" + "="*80)
print("CLAUDE RESPONSE:")
print("="*80)
print(response.content)
print("="*80)

# Save to file
debug_file = Path(__file__).parent / "responses" / "claude_stage1_actual.txt"
debug_file.write_text(response.content, encoding='utf-8')
print(f"\nSaved to: {debug_file}")
