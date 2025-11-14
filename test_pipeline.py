"""
Test script for Network CCE Pipeline

Tests the complete 4-stage assessment workflow with sample configurations.
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from cce_inspector.core.config import CCEConfig, get_config
from cce_inspector.core.ai_clients import create_ai_client
from cce_inspector.plugins.network import NetworkCCEPipeline, run_network_assessment
from cce_inspector.core.utils import get_logger
from cce_inspector.core.report_generator import generate_html_report


def test_pipeline_basic():
    """Test basic pipeline functionality."""
    print("=" * 80)
    print("TEST: Basic Pipeline Functionality")
    print("=" * 80)

    # Load configuration
    try:
        config = get_config()
        print(f"✓ Configuration loaded")
        print(f"  - AI Provider: {config.ai_provider}")
        print(f"  - Output Dir: {config.output_dir}")
    except Exception as e:
        print(f"✗ Failed to load configuration: {str(e)}")
        return False

    # Create AI client
    try:
        ai_client = create_ai_client(config)
        print(f"✓ AI client created: {ai_client.__class__.__name__}")

        # Validate connection
        print("  Validating AI connection...")
        if ai_client.validate_connection():
            print("  ✓ AI connection validated")
        else:
            print("  ✗ AI connection validation failed")
            return False

    except Exception as e:
        print(f"✗ Failed to create AI client: {str(e)}")
        print("  Make sure your API key is set in .env file")
        return False

    # Initialize pipeline
    try:
        pipeline = NetworkCCEPipeline(config, ai_client)
        print(f"✓ Pipeline initialized")
    except Exception as e:
        print(f"✗ Failed to initialize pipeline: {str(e)}")
        return False

    print("\n✓ All basic checks passed!\n")
    return True


def test_sample_config(config_file: Path, config_name: str):
    """Test pipeline with a sample configuration."""
    print("=" * 80)
    print(f"TEST: {config_name}")
    print("=" * 80)
    print(f"Config file: {config_file}\n")

    if not config_file.exists():
        print(f"✗ Configuration file not found: {config_file}")
        return False

    try:
        # Run assessment
        print("Starting assessment pipeline...")
        result = run_network_assessment(
            config_text=config_file.read_text(encoding='utf-8'),
            save_output=True
        )

        # Display results
        print("\n" + "=" * 80)
        print("ASSESSMENT RESULTS")
        print("=" * 80)

        print(f"\n📋 Asset Information:")
        print(f"  Hostname:     {result.asset_info.hostname}")
        print(f"  Vendor:       {result.asset_info.vendor}")
        print(f"  OS Type:      {result.asset_info.os_type}")
        print(f"  OS Version:   {result.asset_info.os_version}")
        print(f"  Device Type:  {result.asset_info.device_type}")
        print(f"  Device Role:  {result.asset_info.device_role}")

        # Handle both numeric and string confidence values
        conf = result.asset_info.confidence
        if isinstance(conf, (int, float)):
            print(f"  Confidence:   {conf:.2%}")
        else:
            print(f"  Confidence:   {conf}")

        summary = result.assessment_result.get_summary()
        print(f"\n📊 Assessment Summary:")
        print(f"  Total Checks:    {summary['total_checks']}")
        print(f"  ✓ Passed:        {summary['passed']} ({summary['pass_percentage']:.1f}%)")
        print(f"  ✗ Failed:        {summary['failed']} ({summary['fail_percentage']:.1f}%)")
        print(f"  ? Manual Review: {summary['manual_review']}")
        print(f"  Average Score:   {summary['average_score']:.1f}/100")

        print(f"\n⏱️  Execution Time:")
        print(f"  Total: {result.execution_time:.2f} seconds")

        # Show critical findings
        critical = result.assessment_result.get_critical_findings()
        if critical:
            print(f"\n⚠️  Critical Findings (top 5):")
            for i, finding in enumerate(critical[:5], 1):
                print(f"  {i}. {finding.check_id}: {finding.findings[:80]}...")

        print(f"\n✓ Test completed successfully!")
        from cce_inspector.core.config import get_config
        cfg = get_config()
        print(f"  Results saved to: {cfg.output_dir}")

        return True

    except Exception as e:
        print(f"\n✗ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "CCE INSPECTOR - PIPELINE TEST" + " " * 29 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")

    # Test 1: Basic functionality
    if not test_pipeline_basic():
        print("\n✗ Basic tests failed. Please check your configuration.")
        return

    # Get sample configs path
    samples_dir = Path("cce_inspector/plugins/network/samples")

    # Test 2: Cisco IOS Vulnerable
    print("\n")
    cisco_vuln = samples_dir / "cisco_ios_vulnerable.cfg"
    test_sample_config(cisco_vuln, "Cisco IOS Vulnerable Configuration")

    # Test 3: Cisco IOS Secure
    print("\n")
    cisco_secure = samples_dir / "cisco_ios_secure.cfg"
    test_sample_config(cisco_secure, "Cisco IOS Secure Configuration")

    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 28 + "ALL TESTS COMPLETED" + " " * 31 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")


if __name__ == "__main__":
    main()
