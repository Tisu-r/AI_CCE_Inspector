"""
Ollama Direct Test Script

Tests Ollama responses and saves debug information to files.
"""

import sys
import json
from pathlib import Path
from datetime import datetime

# Add project to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from cce_inspector.core.ai_clients.local_llm_client import LocalLLMClient
from cce_inspector.core.utils import FileHandler


def save_debug_output(filename: str, content: str):
    """Save debug output to file."""
    debug_dir = Path(__file__).parent / "responses"
    debug_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = debug_dir / f"{timestamp}_{filename}"

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  💾 Saved to: {filepath}")
    return filepath


def test_1_simple_prompt():
    """Test 1: Simple prompt to verify Ollama is working."""
    print("\n" + "=" * 80)
    print("TEST 1: Simple Prompt - Verify Ollama Basic Functionality")
    print("=" * 80)

    try:
        client = LocalLLMClient(
            server_url="http://localhost:11434",
            model="gpt-oss:20b",
            temperature=0.1
        )

        print("✓ Client created")

        # Simple test prompt
        prompt = "Say 'Hello, I am working!' in JSON format: {\"message\": \"your response here\"}"

        print(f"📤 Sending prompt: {prompt[:100]}...")

        response = client.generate(prompt)

        print(f"\n📥 Response received:")
        print(f"  Model: {response.model}")
        print(f"  Tokens: {response.tokens_used}")
        print(f"  Finish reason: {response.finish_reason}")
        print(f"\n  Content ({len(response.content)} chars):")
        print(f"  {'-' * 76}")
        print(f"  {response.content}")
        print(f"  {'-' * 76}")

        # Save response
        save_debug_output("test1_simple.txt", response.content)

        # Try to parse as JSON
        try:
            parsed = json.loads(response.content)
            print(f"\n  ✓ Valid JSON!")
            print(f"    Parsed: {parsed}")
        except json.JSONDecodeError as e:
            print(f"\n  ✗ Not valid JSON: {str(e)}")

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_2_json_response():
    """Test 2: Request structured JSON response."""
    print("\n" + "=" * 80)
    print("TEST 2: JSON Response - Request Structured Data")
    print("=" * 80)

    try:
        client = LocalLLMClient(
            server_url="http://localhost:11434",
            model="gpt-oss:20b",
            temperature=0.1
        )

        prompt = """Please respond with ONLY valid JSON (no other text):
{
  "device": "router",
  "vendor": "cisco",
  "status": "test successful"
}

Respond with ONLY the JSON above, nothing else."""

        print(f"📤 Sending JSON request prompt...")

        response = client.generate(prompt)

        print(f"\n📥 Response content ({len(response.content)} chars):")
        print(f"  {'-' * 76}")
        print(f"  {response.content}")
        print(f"  {'-' * 76}")

        # Save response
        save_debug_output("test2_json_request.txt", response.content)

        # Try to parse
        try:
            parsed = json.loads(response.content)
            print(f"\n  ✓ Valid JSON!")
            print(f"    {json.dumps(parsed, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"\n  ✗ Not valid JSON: {str(e)}")

            # Try to extract JSON
            print(f"\n  Attempting to extract JSON from response...")
            import re
            json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group(0))
                    print(f"  ✓ Extracted and parsed JSON:")
                    print(f"    {json.dumps(parsed, indent=2)}")
                except:
                    print(f"  ✗ Extraction failed")

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_3_stage1_prompt():
    """Test 3: Actual Stage 1 prompt with small config."""
    print("\n" + "=" * 80)
    print("TEST 3: Stage 1 Prompt - Asset Identification")
    print("=" * 80)

    try:
        client = LocalLLMClient(
            server_url="http://localhost:11434",
            model="gpt-oss:20b",
            temperature=0.1,
            max_tokens=2048
        )

        # Load actual Stage 1 prompt template
        template_path = project_root / "cce_inspector/templates/prompts/stage1_asset_identification.txt"
        template = FileHandler.read_text(template_path)

        # Simple Cisco config for testing
        test_config = """
version 15.2
service timestamps debug datetime msec
service timestamps log datetime msec
!
hostname TEST-ROUTER
!
interface GigabitEthernet0/0
 description WAN Interface
 ip address 192.168.1.1 255.255.255.0
!
end
"""

        prompt = template.replace("{{CONFIGURATION}}", test_config)

        print(f"📤 Sending Stage 1 prompt...")
        print(f"  Template length: {len(template)} chars")
        print(f"  Full prompt length: {len(prompt)} chars")

        response = client.generate(
            prompt=prompt,
            system_prompt="You are a network security expert analyzing device configurations."
        )

        print(f"\n📥 Response received ({len(response.content)} chars):")
        print(f"  {'-' * 76}")
        print(f"  {response.content[:500]}...")
        print(f"  {'-' * 76}")

        # Save full response
        filepath = save_debug_output("test3_stage1_response.txt", response.content)

        # Save prompt too
        save_debug_output("test3_stage1_prompt.txt", prompt)

        # Try to parse as JSON
        try:
            # Try cleaning first
            cleaned = response.content.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            parsed = json.loads(cleaned)
            print(f"\n  ✓ Valid JSON after cleaning!")
            print(f"    Keys: {list(parsed.keys())}")

            # Check required fields
            required = ["vendor", "os_type", "os_version", "hostname", "device_type", "device_role", "confidence"]
            missing = [k for k in required if k not in parsed]

            if missing:
                print(f"    ✗ Missing required fields: {missing}")
            else:
                print(f"    ✓ All required fields present!")
                print(f"\n    Asset Info:")
                for key in required:
                    print(f"      {key}: {parsed[key]}")

        except json.JSONDecodeError as e:
            print(f"\n  ✗ JSON parsing failed: {str(e)}")
            print(f"    Response starts with: {response.content[:100]}")

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_4_model_info():
    """Test 4: Get model information."""
    print("\n" + "=" * 80)
    print("TEST 4: Model Information")
    print("=" * 80)

    try:
        client = LocalLLMClient(
            server_url="http://localhost:11434",
            model="gpt-oss:20b"
        )

        # List available models
        print("📋 Available models:")
        models = client.list_available_models()
        for model in models:
            marker = "👉" if "gpt-oss:20b" in model else "  "
            print(f"  {marker} {model}")

        # Get model info
        print(f"\n📊 Model info for gpt-oss:20b:")
        info = client.get_model_info()
        for key, value in info.items():
            if key == "model_info":
                continue  # Skip large nested dict
            print(f"  {key}: {value}")

        return True

    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Ollama tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 25 + "OLLAMA DEBUG TESTS" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")

    results = []

    # Test 1: Simple prompt
    results.append(("Simple Prompt", test_1_simple_prompt()))

    # Test 2: JSON response
    results.append(("JSON Response", test_2_json_response()))

    # Test 3: Stage 1 prompt
    results.append(("Stage 1 Prompt", test_3_stage1_prompt()))

    # Test 4: Model info
    results.append(("Model Info", test_4_model_info()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {name}")

    print(f"\n📁 Debug outputs saved to: {Path(__file__).parent / 'responses'}")
    print("\n")


if __name__ == "__main__":
    main()
