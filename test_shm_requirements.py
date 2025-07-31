#!/usr/bin/env python3
"""
Test script to determine shared memory usage and requirements
"""

import os
import subprocess
import time

def check_shm_usage():
    """Check current shared memory usage"""
    try:
        # Check /dev/shm usage
        result = subprocess.run(['df', '-h', '/dev/shm'], capture_output=True, text=True)
        print("📊 Current /dev/shm usage:")
        print(result.stdout)
        
        # Check available vs used
        lines = result.stdout.strip().split('\n')
        if len(lines) > 1:
            data = lines[1].split()
            size = data[1]
            used = data[2]
            available = data[3]
            print(f"   Size: {size}, Used: {used}, Available: {available}")
            
    except Exception as e:
        print(f"❌ Error checking /dev/shm: {e}")

def test_browser_load():
    """Test browser memory usage with different workloads"""
    print("\n🌐 Testing browser memory usage...")
    
    # Check Chrome processes
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        chrome_processes = [line for line in result.stdout.split('\n') if 'chromium' in line.lower()]
        print(f"🔍 Found {len(chrome_processes)} Chrome processes")
        
        # Calculate total memory usage
        total_memory = 0
        for process in chrome_processes:
            parts = process.split()
            if len(parts) > 5:
                try:
                    memory_kb = float(parts[5])  # RSS in KB
                    total_memory += memory_kb
                except:
                    pass
        
        total_memory_mb = total_memory / 1024
        print(f"📈 Total Chrome memory usage: {total_memory_mb:.1f} MB")
        
    except Exception as e:
        print(f"❌ Error checking Chrome processes: {e}")

def test_recommendations():
    """Provide recommendations based on usage"""
    print("\n💡 Shared Memory Recommendations:")
    print("┌─────────────────┬──────────────────┬─────────────────────────────┐")
    print("│ Use Case        │ Recommended Size │ Docker Flag                 │")
    print("├─────────────────┼──────────────────┼─────────────────────────────┤")
    print("│ Basic automation│ 512MB           │ --shm-size=512m             │")
    print("│ HubSpot (simple)│ 1GB             │ --shm-size=1g               │")
    print("│ HubSpot (full)  │ 2GB             │ --shm-size=2g (current)     │")
    print("│ Multiple tabs   │ 4GB             │ --shm-size=4g               │")
    print("└─────────────────┴──────────────────┴─────────────────────────────┘")

def main():
    print("🧪 Testing Shared Memory Requirements for Browser Automation")
    print("=" * 60)
    
    # Check current environment
    print(f"🐳 Running in Docker: {'CONTAINER' in os.environ or os.path.exists('/.dockerenv')}")
    
    # Check shared memory
    check_shm_usage()
    
    # Test browser load
    test_browser_load()
    
    # Provide recommendations
    test_recommendations()
    
    print("\n🔧 How to test different sizes:")
    print("1. Stop your current container")
    print("2. Try with smaller size:")
    print("   docker run --shm-size=512m ...")
    print("3. Monitor for crashes or errors")
    print("4. Increase if needed")
    
    print("\n⚠️  Signs you need more shared memory:")
    print("   • Random browser crashes")
    print("   • 'DevToolsActivePort file doesn't exist' errors")
    print("   • Slow page rendering")
    print("   • Failed automation scripts")

if __name__ == "__main__":
    main() 