"""
Setup guide for using Ollama with the Travel Booking Agent.
"""

import subprocess
import sys
import asyncio
import aiohttp


async def check_ollama_status():
    """Check if Ollama is running and accessible"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    print("✓ Ollama is running")
                    print(f"✓ Found {len(models)} installed models:")
                    for model in models:
                        name = model.get("name", "Unknown")
                        size = model.get("size", 0) / (1024**3)  # Convert to GB
                        print(f"  - {name} ({size:.1f}GB)")
                    return True, models
                else:
                    print("✗ Ollama is not responding properly")
                    return False, []
    except Exception as e:
        print(f"✗ Cannot connect to Ollama: {e}")
        return False, []


def install_ollama():
    """Provide instructions for installing Ollama"""
    print("Ollama Installation Instructions:")
    print("=" * 40)
    print()
    print("1. Visit https://ollama.ai and download Ollama for your OS")
    print("2. Or use these commands:")
    print()
    print("   macOS/Linux:")
    print("   curl -fsSL https://ollama.ai/install.sh | sh")
    print()
    print("   Windows:")
    print("   Download from https://ollama.ai/download/windows")
    print()
    print("3. Start Ollama:")
    print("   ollama serve")
    print()
    print("4. Install a model:")
    print("   ollama pull llama3.1")


def recommend_models():
    """Recommend models for travel booking assistant"""
    print("Recommended Models for Travel Booking:")
    print("=" * 40)
    print()
    print("🚀 FAST & EFFICIENT:")
    print("   ollama pull llama3.1:8b     # 8B parameters, good balance")
    print("   ollama pull qwen2.5:7b      # Fast and capable")
    print()
    print("🎯 BEST PERFORMANCE:")
    print("   ollama pull llama3.1        # 70B parameters, most capable")
    print("   ollama pull qwen2.5:14b     # Good reasoning abilities")
    print()
    print("⚡ LIGHTWEIGHT:")
    print("   ollama pull llama3.1:1b     # Very fast, basic capabilities")
    print("   ollama pull phi3:mini       # Microsoft's efficient model")
    print()
    print("🔧 SPECIALIZED:")
    print("   ollama pull mistral         # Good for structured tasks")
    print("   ollama pull codellama       # If you need code generation")


async def test_model_performance():
    """Test different models for travel booking tasks"""
    models_to_test = [
        "qwen2.5:7b-instruct",
        "gemma3:1b",
        "deepseek-r1:latest",
        "llama3.1:8b",
        "phi3:mini",
    ]

    print("Testing Model Performance:")
    print("=" * 40)

    test_prompt = "You are a travel assistant. A customer asks: 'Find me a hotel in Miami under $200 per night.' How would you respond?"

    for model in models_to_test:
        print(f"\nTesting {model}...")
        try:
            from llama_index.llms.ollama import Ollama

            llm = Ollama(model=model, base_url="http://localhost:11434")

            import time

            start_time = time.time()
            response = await llm.acomplete(test_prompt)
            end_time = time.time()

            print(f"✓ {model}: {end_time - start_time:.1f}s")
            print(f"  Response length: {len(str(response))} chars")

        except Exception as e:
            print(f"✗ {model}: {e}")


async def main():
    """Main setup function"""
    print("Ollama Setup Guide for Travel Booking Agent")
    print("=" * 50)

    # Check if Ollama is running
    is_running, models = await check_ollama_status()

    if not is_running:
        print("\nOllama is not running or not installed.")
        install_ollama()
        return

    if not models:
        print("\nNo models installed.")
        recommend_models()
        print("\nAfter installing a model, run this script again.")
        return

    print("\n✓ Ollama setup looks good!")

    # Check for recommended models
    model_names = [m.get("name", "") for m in models]
    recommended = ["llama3.1", "llama3.1:8b", "qwen2.5:7b", "mistral"]

    has_recommended = any(rec in model_names for rec in recommended)

    if not has_recommended:
        print("\nRecommendation: Install a model optimized for chat:")
        recommend_models()

    # Offer to test models
    if len(models) > 0:
        test_choice = input(
            "\nWould you like to test model performance? (y/n): "
        ).lower()
        if test_choice == "y":
            await test_model_performance()

    print("\n" + "=" * 50)
    print("Setup Complete! You can now run:")
    print("python travel_agent_example.py interactive")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
