#!/usr/bin/env python3
"""
Test script for text-to-Live2D modeling
"""

import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from live2d_ai import Live2DModelGenerator

async def main():
    parser = argparse.ArgumentParser(description="Test text-to-Live2D generation")
    parser.add_argument("--prompt", required=True, help="Character description")
    parser.add_argument("--style", default="anime", help="Art style")
    args = parser.parse_args()
    
    generator = Live2DModelGenerator(
        api_endpoint="http://localhost:8080"
    )
    
    print(f"🎨 Generating Live2D model from: {args.prompt}")
    print(f"🎨 Style: {args.style}")
    
    result = await generator.text_to_live2d(
        text_description=args.prompt,
        style=args.style,
        auto_rig=True,
        generate_physics=True
    )
    
    print("\n✅ Model generated!")
    print(f"📦 Model path: {result.model_path}")
    print(f"🖼️  Preview: {result.preview_url}")
    print(f"⏱️  Generation time: {result.generation_time:.1f}s")
    
    print("\n📊 Parameters:")
    for key, value in result.parameters.items():
        print(f"   - {key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())
