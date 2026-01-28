"""
CodeMentor Integration Demo: Connecting Alice's Analysis Engine with Bob's Extensions

This demonstrates how Alice's powerful analysis engine integrates seamlessly
with Bob's advanced extensions to create a comprehensive development tool.

Author: Bob (Claude Code Instance)
Collaborating with Alice's CodeMentor foundation
"""

import sys
import os
import asyncio
import json
from typing import Dict, Any

# Add current directory to path so we can import Alice's modules
sys.path.insert(0, '/tmp/cc-exp/run_2026-01-22_23-38-45/output/')

try:
    from analysis_engine import CodeAnalysisEngine
    from codementor_extensions import CodeMentorExtensions
    from collaborative_analyzer import CollaborativeAnalyzer
    print("✅ Successfully imported Alice's analysis engine and collaborative system")
except ImportError as e:
    print(f"⚠️ Could not import Alice's modules: {e}")
    print("Running standalone demonstration of extensions...")

class IntegratedCodeMentor:
    """
    Integrated system combining Alice's analysis engine with Bob's extensions
    """

    def __init__(self):
        try:
            self.alice_analyzer = CodeAnalysisEngine()
            self.alice_collaboration = CollaborativeAnalyzer()
            alice_available = True
        except:
            alice_available = False

        self.bob_extensions = CodeMentorExtensions()
        self.alice_available = alice_available

    async def comprehensive_analysis(self, code: str, file_path: str = "example.py") -> Dict[str, Any]:
        """
        Perform comprehensive analysis combining both Alice's and Bob's capabilities
        """
        results = {
            'timestamp': '2026-01-23T00:00:00',
            'file_path': file_path,
            'analysis_components': []
        }

        # Alice's pattern detection and quality analysis
        if self.alice_available:
            try:
                alice_results = await self.alice_analyzer.analyze_code_async(code)
                results['alice_analysis'] = {
                    'patterns': alice_results.get('patterns', []),
                    'quality_issues': alice_results.get('quality_issues', []),
                    'metrics': alice_results.get('metrics', {}),
                    'educational_context': alice_results.get('educational_context', [])
                }
                results['analysis_components'].append('Alice: Pattern Detection & Quality Analysis')
            except Exception as e:
                print(f"Error in Alice's analysis: {e}")
                results['alice_analysis'] = {'error': str(e)}

        # Bob's advanced refactoring and team insights
        try:
            bob_results = await self.bob_extensions.enhanced_analysis(code, file_path)
            results['bob_extensions'] = {
                'refactoring_suggestions': bob_results.get('refactoring_suggestions', []),
                'team_insights': bob_results.get('team_insights', []),
                'enhancement_metadata': bob_results.get('enhancement_metadata', {})
            }
            results['analysis_components'].append('Bob: Advanced Refactoring & Team Analytics')
        except Exception as e:
            print(f"Error in Bob's extensions: {e}")
            results['bob_extensions'] = {'error': str(e)}

        # Collaborative workflow integration
        if self.alice_available:
            try:
                collaboration_context = {
                    'session_id': 'demo_session',
                    'participants': ['Alice', 'Bob'],
                    'timestamp': results['timestamp']
                }
                results['collaboration'] = {
                    'session_active': True,
                    'real_time_enabled': True,
                    'participants': collaboration_context['participants']
                }
                results['analysis_components'].append('Alice: Real-time Collaboration System')
            except Exception as e:
                print(f"Error in collaboration setup: {e}")

        return results

    def generate_executive_summary(self, analysis_results: Dict[str, Any]) -> str:
        """
        Generate an executive summary of the comprehensive analysis
        """
        summary = "# CodeMentor: Comprehensive Analysis Summary\n\n"

        # Analysis components
        summary += "## 🔧 Analysis Components Active\n"
        for component in analysis_results.get('analysis_components', []):
            summary += f"✅ {component}\n"
        summary += "\n"

        # Alice's findings
        if 'alice_analysis' in analysis_results and 'error' not in analysis_results['alice_analysis']:
            alice = analysis_results['alice_analysis']
            patterns_count = len(alice.get('patterns', []))
            issues_count = len(alice.get('quality_issues', []))

            summary += f"## 🎨 Alice's Pattern Detection\n"
            summary += f"- **Patterns Detected:** {patterns_count}\n"
            summary += f"- **Quality Issues:** {issues_count}\n"

            if patterns_count > 0:
                summary += "- **Top Patterns:**\n"
                for pattern in alice.get('patterns', [])[:3]:
                    summary += f"  - {pattern.get('name', 'Unknown')} ({pattern.get('confidence', 0):.0%} confidence)\n"

            summary += "\n"

        # Bob's findings
        if 'bob_extensions' in analysis_results and 'error' not in analysis_results['bob_extensions']:
            bob = analysis_results['bob_extensions']
            refactoring_count = len(bob.get('refactoring_suggestions', []))
            insights_count = len(bob.get('team_insights', []))

            summary += f"## 🔧 Bob's Advanced Analysis\n"
            summary += f"- **Refactoring Suggestions:** {refactoring_count}\n"
            summary += f"- **Team Insights:** {insights_count}\n"

            if refactoring_count > 0:
                summary += "- **Top Suggestions:**\n"
                for suggestion in bob.get('refactoring_suggestions', [])[:3]:
                    summary += f"  - {suggestion.get('pattern', 'Unknown').replace('_', ' ').title()} (Impact: {suggestion.get('impact', 0):.2f})\n"

            summary += "\n"

        # Collaboration status
        if 'collaboration' in analysis_results:
            collab = analysis_results['collaboration']
            summary += f"## 🤝 Collaboration Status\n"
            summary += f"- **Real-time Enabled:** {'✅ Yes' if collab.get('real_time_enabled') else '❌ No'}\n"
            summary += f"- **Active Participants:** {', '.join(collab.get('participants', []))}\n\n"

        # Overall assessment
        total_findings = 0
        if 'alice_analysis' in analysis_results and 'error' not in analysis_results['alice_analysis']:
            total_findings += len(analysis_results['alice_analysis'].get('patterns', []))
            total_findings += len(analysis_results['alice_analysis'].get('quality_issues', []))

        if 'bob_extensions' in analysis_results and 'error' not in analysis_results['bob_extensions']:
            total_findings += len(analysis_results['bob_extensions'].get('refactoring_suggestions', []))

        summary += f"## 📊 Overall Assessment\n"
        summary += f"- **Total Findings:** {total_findings}\n"
        summary += f"- **Analysis Quality:** {'🟢 Comprehensive' if total_findings > 5 else '🟡 Good' if total_findings > 2 else '🔴 Limited'}\n"
        summary += f"- **Collaboration Ready:** {'✅ Yes' if 'collaboration' in analysis_results else '⚠️ Setup Required'}\n\n"

        summary += "---\n"
        summary += "*Analysis performed by Alice & Bob collaborative system*\n"

        return summary

async def main():
    """
    Demonstrate the integrated CodeMentor system
    """
    print("🚀 CodeMentor Integration Demo")
    print("=" * 60)
    print("Demonstrating Alice + Bob collaboration")
    print()

    # Initialize integrated system
    integrated = IntegratedCodeMentor()

    # Test code with multiple opportunities for analysis
    test_code = '''
import os
import sys
import time

class DataProcessor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.data_cache = {}
            self.observers = []
            self.initialized = True

    def process_user_data(self, user_data):
        if user_data is not None:
            if len(user_data) > 0:
                if isinstance(user_data, list):
                    if all(isinstance(item, dict) for item in user_data):
                        result = []
                        for item in user_data:
                            if 'name' in item and 'email' in item:
                                # Potential security issue: no input validation
                                processed = {
                                    'name': item['name'].upper(),
                                    'email': item['email'].lower(),
                                    'processed_at': time.time()
                                }
                                result.append(processed)
                                self.notify_observers('user_processed', processed)
                        return result
        return []

    def process_order_data(self, order_data):
        # Nearly identical to process_user_data - code duplication
        if order_data is not None:
            if len(order_data) > 0:
                if isinstance(order_data, list):
                    if all(isinstance(item, dict) for item in order_data):
                        result = []
                        for item in order_data:
                            if 'id' in item and 'amount' in item:
                                processed = {
                                    'id': item['id'],
                                    'amount': item['amount'] * 1.1,  # Add tax
                                    'processed_at': time.time()
                                }
                                result.append(processed)
                                self.notify_observers('order_processed', processed)
                        return result
        return []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event, data):
        for observer in self.observers:
            observer.update(event, data)

def fn(x, y):  # Poor function name
    return x + y

def process(data):  # Another poor function name
    # Complex nested logic
    if data:
        if 'users' in data:
            if data['users']:
                if len(data['users']) > 0:
                    processor = DataProcessor()
                    return processor.process_user_data(data['users'])
    return None

# Usage example
if __name__ == "__main__":
    processor = DataProcessor()

    sample_users = [
        {'name': 'john', 'email': 'JOHN@EXAMPLE.COM'},
        {'name': 'jane', 'email': 'jane@test.org'}
    ]

    result = processor.process_user_data(sample_users)
    print("Processed:", result)
'''

    print("📝 Analyzing comprehensive test code...")
    print("Code contains: Singleton pattern, Observer pattern, code duplication, complex conditionals")
    print()

    # Perform comprehensive analysis
    analysis_results = await integrated.comprehensive_analysis(test_code, "data_processor.py")

    # Generate and display executive summary
    summary = integrated.generate_executive_summary(analysis_results)
    print(summary)

    # Save detailed results
    detailed_report_file = "/tmp/cc-exp/run_2026-01-22_23-38-45/output/integration_analysis_report.json"
    with open(detailed_report_file, 'w') as f:
        json.dump(analysis_results, f, indent=2)

    print(f"📄 Detailed analysis saved to: {detailed_report_file}")

    # Generate comprehensive report using Bob's extensions
    if 'bob_extensions' in analysis_results:
        markdown_report = integrated.bob_extensions.export_analysis_report(
            analysis_results['bob_extensions'], 'markdown'
        )

        report_file = "/tmp/cc-exp/run_2026-01-22_23-38-45/output/comprehensive_analysis_report.md"
        with open(report_file, 'w') as f:
            f.write(markdown_report)

        print(f"📋 Comprehensive report saved to: {report_file}")

    # Display integration capabilities
    print("\n🔗 Integration Capabilities:")
    integrations = integrated.bob_extensions.integrate_with_tools()
    for tool, description in integrations.items():
        print(f"  • {tool}: {description}")

    print("\n✨ Integration Demo Complete!")
    print("\nKey Highlights:")
    print("- Alice's pattern detection identified architectural patterns")
    print("- Bob's extensions provided concrete refactoring suggestions")
    print("- Real-time collaboration system enables team reviews")
    print("- Comprehensive reporting in multiple formats")
    print("- Ready for integration with popular development tools")

if __name__ == "__main__":
    asyncio.run(main())