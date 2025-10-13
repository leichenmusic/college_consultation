#!/usr/bin/env python3
"""
PM Agent CLI Tool
Test and interact with the Product Manager Agent
"""

import sys
import json
import argparse
from database import db_manager
from pm_agent import get_pm_agent, analyze_session_for_insights

def main():
    parser = argparse.ArgumentParser(description='PM Agent CLI Tool')
    parser.add_argument('command', choices=['analysis', 'roadmap', 'insights', 'export', 'add-feature'], 
                       help='Command to execute')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json',
                       help='Output format for export')
    parser.add_argument('--feature-file', help='JSON file with feature data for add-feature command')
    
    args = parser.parse_args()
    
    # Initialize PM Agent
    pm_agent = get_pm_agent(db_manager)
    if not pm_agent:
        print("❌ Failed to initialize PM Agent")
        return 1
    
    try:
        if args.command == 'analysis':
            print("📊 Generating Strategic Analysis...")
            analysis = pm_agent.generate_strategic_analysis()
            print(json.dumps(analysis, indent=2, ensure_ascii=False))
            
        elif args.command == 'roadmap':
            print("🗺️ Product Roadmap:")
            roadmap = pm_agent.get_product_roadmap()
            
            for status, features in roadmap.items():
                status_titles = {
                    "now": "🚀 In Progress",
                    "next": "📋 Planned Next", 
                    "later": "🔮 Future",
                    "launched": "✅ Launched"
                }
                
                print(f"\n{status_titles.get(status, status.title())}:")
                print("=" * 50)
                
                if not features:
                    print("  (No features)")
                    continue
                    
                for feature in features:
                    priority_emoji = {
                        "critical": "🔥",
                        "high": "⚡", 
                        "medium": "📊",
                        "low": "💡"
                    }
                    
                    print(f"  {priority_emoji.get(feature.priority.value, '📋')} {feature.name}")
                    print(f"     {feature.description}")
                    print(f"     Priority: {feature.priority.value} | Effort: {feature.estimated_effort} pts | Value: {feature.business_value}/10")
                    if feature.target_users:
                        print(f"     Users: {', '.join(feature.target_users)}")
                    print()
                    
        elif args.command == 'insights':
            print("💡 Analyzing User Insights...")
            # Mock session data for testing
            session_data = {
                "user_profile": {
                    "name": "Test User",
                    "form_completed": True,
                    "current_grade": "本科在读",
                    "countries": ["美国", "英国"]
                },
                "chat_history": [
                    {"sender": "user", "message": "Hi"},
                    {"sender": "assistant", "message": "Hello!"},
                    {"sender": "user", "message": "Help"}
                ]
            }
            
            insights = analyze_session_for_insights(session_data, db_manager)
            print(json.dumps(insights, indent=2, ensure_ascii=False))
            
        elif args.command == 'export':
            print(f"📤 Exporting roadmap as {args.format}...")
            content = pm_agent.export_roadmap(args.format)
            
            filename = f"roadmap_export.{args.format}"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Exported to {filename}")
            
        elif args.command == 'add-feature':
            if not args.feature_file:
                print("❌ --feature-file required for add-feature command")
                return 1
                
            try:
                with open(args.feature_file, 'r', encoding='utf-8') as f:
                    feature_data = json.load(f)
                
                feature = pm_agent.add_feature(feature_data)
                print(f"✅ Added feature: {feature.name}")
                print(f"   ID: {feature.id}")
                print(f"   Priority: {feature.priority.value}")
                print(f"   Status: {feature.status.value}")
                
            except FileNotFoundError:
                print(f"❌ Feature file not found: {args.feature_file}")
                return 1
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in feature file: {args.feature_file}")
                return 1
                
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
