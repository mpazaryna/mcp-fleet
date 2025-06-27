#!/usr/bin/env python3
"""
Simple test script to verify the template system is working
"""
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.template_engine import create_template_engine
from src.pattern_manager import create_pattern_manager, PatternRenderContext, ExplorationInsights
from src.prompt_manager import create_prompt_manager, MethodologyPhase, ConversationContext


async def test_template_engine():
    """Test basic template engine functionality"""
    print("🔧 Testing Template Engine...")
    
    base_path = Path(__file__).parent
    engine = await create_template_engine(base_path)
    
    # Test loading a pattern
    pattern = await engine.load_template("patterns/software/product_requirement_doc.md")
    if pattern:
        print(f"✅ Loaded pattern: {pattern.metadata.name}")
        print(f"   Domain: {pattern.metadata.domain}")
        print(f"   Variables: {len(pattern.metadata.variables)}")
    else:
        print("❌ Failed to load pattern")
    
    # Test loading a prompt
    prompt = await engine.load_template("prompts/exploration.md")
    if prompt:
        print(f"✅ Loaded prompt: {prompt.metadata.name}")
        print(f"   Content length: {len(prompt.content)}")
    else:
        print("❌ Failed to load prompt")


async def test_pattern_manager():
    """Test pattern manager functionality"""
    print("\n📋 Testing Pattern Manager...")
    
    base_path = Path(__file__).parent
    pattern_manager = await create_pattern_manager(base_path)
    
    # Test loading patterns by domain
    software_patterns = await pattern_manager.get_patterns_by_domain("software")
    print(f"✅ Found {len(software_patterns)} software patterns")
    
    if software_patterns:
        # Test rendering a specification
        context = PatternRenderContext(
            project_name="Test Project",
            domain="software", 
            pattern_name="product_requirement_doc",
            exploration_insights=ExplorationInsights(
                user_pain_points="Users struggle with complex workflows",
                goals="Simplify the user experience",
                technical_considerations="Must integrate with existing API"
            )
        )
        
        rendered = await pattern_manager.render_specification(context)
        if rendered:
            print(f"✅ Rendered specification ({len(rendered)} chars)")
            print(f"   Preview: {rendered[:100]}...")
        else:
            print("❌ Failed to render specification")


async def test_prompt_manager():
    """Test prompt manager functionality"""
    print("\n💬 Testing Prompt Manager...")
    
    base_path = Path(__file__).parent
    prompt_manager = await create_prompt_manager(base_path)
    
    # Test getting exploration prompt
    context = ConversationContext(
        project_name="Test Project",
        current_phase=MethodologyPhase.EXPLORATION,
        project_description="A test project for validation"
    )
    
    exploration_prompt = await prompt_manager.get_exploration_prompt(context)
    if exploration_prompt:
        print(f"✅ Generated exploration prompt ({len(exploration_prompt)} chars)")
        print(f"   Preview: {exploration_prompt[:100]}...")
    else:
        print("❌ Failed to generate exploration prompt")
    
    # Test available prompts
    available_prompts = await prompt_manager.list_available_prompts()
    print(f"✅ Found {len(available_prompts)} available prompts")


async def main():
    """Run all tests"""
    print("🚀 Testing Template System\n")
    
    try:
        await test_template_engine()
        await test_pattern_manager()
        await test_prompt_manager()
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())