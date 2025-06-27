#!/usr/bin/env python3
"""
Validate that the template system is working for Docker builds
"""
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from template_engine import create_template_engine


async def validate_templates():
    """Validate that templates are loaded and working"""
    print("🔧 Validating Template System...")
    
    base_path = Path(__file__).parent
    engine = await create_template_engine(base_path)
    
    # Test loading patterns
    patterns = await engine.list_templates()
    pattern_count = len([p for p in patterns if p.metadata.domain])
    prompt_count = len([p for p in patterns if 'prompt' in str(p.file_path).lower()])
    
    print(f"✅ Found {pattern_count} patterns and {prompt_count} prompts")
    
    # Test specific pattern
    business_pattern = await engine.load_template("patterns/business/business_process_analysis.md")
    if business_pattern:
        print(f"✅ Business pattern loaded: {business_pattern.metadata.name}")
        print(f"   Variables: {len(business_pattern.metadata.variables)}")
        print(f"   Sections: {len(business_pattern.metadata.sections)}")
    else:
        print("❌ Failed to load business pattern")
        return False
    
    # Test prompt loading  
    exploration_prompt = await engine.load_template("prompts/exploration.md")
    if exploration_prompt:
        print(f"✅ Exploration prompt loaded ({len(exploration_prompt.content)} chars)")
    else:
        print("❌ Failed to load exploration prompt")
        return False
    
    # Test template rendering
    test_variables = {
        "PROJECT_NAME": "Test Business Process",
        "GOALS": "Improve efficiency and reduce costs", 
        "USER_PAIN_POINTS": "Manual processes are slow and error-prone",
        "STAKEHOLDERS": "Operations team, IT department, management",
        "CURRENT_STATE": "Current process requires manual data entry",
        "CONSTRAINTS": "Budget limitations and legacy system dependencies",
        "CORE_FEATURES": "Automated workflow with approval routing",
        "TECHNICAL_CONSIDERATIONS": "API integration with existing systems",
        "SUCCESS_CRITERIA": "50% reduction in processing time",
        "RISKS": "User adoption and training requirements",
        "EXPLORATION_INSIGHTS": "Gathered from stakeholder interviews"
    }
    
    rendered = await engine.render_template(
        "patterns/business/business_process_analysis.md",
        test_variables,
        validate_required=False
    )
    
    if rendered and len(rendered) > 100:
        print(f"✅ Template rendering successful ({len(rendered)} chars)")
        print(f"   Preview: {rendered[:150]}...")
        return True
    else:
        print("❌ Template rendering failed")
        return False


async def main():
    """Main validation function"""
    try:
        success = await validate_templates()
        if success:
            print("\n🎉 Template validation passed! Ready for Docker build.")
            sys.exit(0)
        else:
            print("\n❌ Template validation failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Validation error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())