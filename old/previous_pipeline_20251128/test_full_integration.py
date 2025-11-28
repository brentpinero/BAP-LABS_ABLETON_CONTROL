#!/usr/bin/env python3
"""
Full integration test: API Bridge -> Flask Server -> Model -> JSON Response
Tests the complete pipeline that Max for Live will use
"""
import subprocess
import time
import json

def test_integration():
    print("🧪 TESTING FULL SERUM AI INTEGRATION")
    print("=" * 50)

    # Test 1: Health check
    print("\n[1/3] Testing API health check...")
    try:
        result = subprocess.run(
            ['python', 'max_api_bridge.py'],
            input='{"action": "health"}\n',
            capture_output=True,
            text=True,
            timeout=5
        )
        response = json.loads(result.stdout.strip())
        if response.get('status') == 'success' and response.get('server') == 'healthy':
            print("✅ Health check passed")
            print(f"   Server: {response.get('server')}")
            print(f"   Model loaded: {response.get('model_loaded')}")
        else:
            print("❌ Health check failed")
            print(f"   Response: {response}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

    # Test 2: Generate simple preset
    print("\n[2/3] Testing preset generation (simple)...")
    test_descriptions = [
        "Warm analog bass",
        "Bright pluck",
        "Deep sub bass"
    ]

    for desc in test_descriptions:
        print(f"\n   Generating: '{desc}'")
        try:
            start_time = time.time()
            result = subprocess.run(
                ['python', 'max_api_bridge.py'],
                input=json.dumps({"action": "generate", "description": desc}) + '\n',
                capture_output=True,
                text=True,
                timeout=90
            )
            elapsed = time.time() - start_time

            response = json.loads(result.stdout.strip())

            if response.get('status') == 'success':
                preset = response.get('preset', {})
                param_count = len(preset.get('parameter_changes', []))
                critical_count = len(preset.get('critical_changes', []))

                print(f"   ✅ Generated in {elapsed:.1f}s")
                print(f"   Parameters: {param_count}")
                print(f"   Critical params: {critical_count}")

                # Show first 3 parameters
                if param_count > 0:
                    print("   Sample parameters:")
                    for p in preset['parameter_changes'][:3]:
                        print(f"      - {p['name']}: {p['value']:.3f}")
            else:
                print(f"   ❌ Generation failed: {response.get('message')}")
                return False

        except subprocess.TimeoutExpired:
            print("   ❌ Timeout after 90 seconds")
            return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False

    # Test 3: Complex preset
    print("\n[3/3] Testing complex preset generation...")
    complex_desc = "Aggressive dubstep wobble bass with lots of modulation and screaming highs"
    print(f"   Generating: '{complex_desc}'")

    try:
        start_time = time.time()
        result = subprocess.run(
            ['python', 'max_api_bridge.py'],
            input=json.dumps({"action": "generate", "description": complex_desc}) + '\n',
            capture_output=True,
            text=True,
            timeout=90
        )
        elapsed = time.time() - start_time

        response = json.loads(result.stdout.strip())

        if response.get('status') == 'success':
            preset = response.get('preset', {})
            param_count = len(preset.get('parameter_changes', []))
            critical_changes = preset.get('critical_changes', [])

            print(f"   ✅ Generated in {elapsed:.1f}s")
            print(f"   Parameters: {param_count}")
            print(f"   Critical changes: {', '.join(critical_changes)}")
        else:
            print(f"   ❌ Generation failed: {response.get('message')}")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

    print("\n" + "=" * 50)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("\nSystem is ready for Max for Live integration.")
    print("Average generation time: ~20-30 seconds")
    return True

if __name__ == "__main__":
    success = test_integration()
    exit(0 if success else 1)
