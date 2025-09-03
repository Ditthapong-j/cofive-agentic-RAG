#!/usr/bin/env python3
"""
Simple test to verify document search is working
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv()

def test_one_question():
    """Test one specific question"""
    
    print("🧪 Testing Single Question")
    print("=" * 40)
    
    try:
        from main import AgenticRAGSystem
        
        # Initialize system
        print("Initializing system...")
        rag_system = AgenticRAGSystem()
        rag_system.initialize_agent()
        print("✅ System ready!")
        
        # Test question
        question = "Python คืออะไร?"
        print(f"\n📝 Question: {question}")
        
        result = rag_system.query(question)
        
        print(f"\n🤖 Answer: {result['answer']}")
        
        # Show intermediate steps
        print(f"\n🔍 Intermediate steps:")
        for i, step in enumerate(result.get('intermediate_steps', []), 1):
            if len(step) >= 2:
                action = step[0]
                output = step[1]
                print(f"  Step {i}: {action.tool} - {action.tool_input}")
                print(f"          Output: {output[:100]}..." if len(output) > 100 else f"          Output: {output}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_one_question()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
