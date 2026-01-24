#!/usr/bin/env python3
"""
Demonstration of our Collaborative Code Analysis Tool
This script shows how Bob and Alice work together to analyze code.
"""

from analyzer_bob import BobAnalyzer
from analyzer_alice import AliceAnalyzer
from synthesis import CollaborativeSynthesis
from reporter import CollaborativeReporter

def demo_analysis():
    """Demonstrate collaborative analysis on sample code."""

    # Sample problematic code for demonstration
    sample_code = '''
def process_user_data(user_input):
    # SQL injection vulnerability
    query = f"SELECT * FROM users WHERE name = '{user_input}'"

    # Inefficient nested loops
    results = []
    for i in range(len(data)):
        for j in range(len(data)):
            if data[i] == user_input:
                results.append(data[j])

    return results

class GodClass:
    """This class does too many things."""
    def __init__(self):
        self.data = []
        self.users = {}
        self.sessions = {}
        self.config = {}

    def do_everything(self, user_input, data, config):
        # Validates users
        # Processes data
        # Manages sessions
        # Updates config
        # Handles database operations
        # Performs calculations
        pass
'''

    print("🤖 Collaborative Code Analysis Demo")
    print("=" * 50)

    # Initialize our analyzers
    bob = BobAnalyzer()
    alice = AliceAnalyzer()
    synthesizer = CollaborativeSynthesis()
    reporter = CollaborativeReporter()

    print("\n🔍 Bob analyzing performance & security...")
    bob_findings = bob.analyze(sample_code, "demo_sample.py")
    print(f"   Found {len(bob_findings)} issues")

    print("\n🔍 Alice analyzing design & quality...")
    alice_findings = alice.analyze(sample_code, "demo_sample.py")
    print(f"   Found {len(alice_findings)} issues")

    print("\n🤝 Synthesizing collaborative insights...")
    synthesis = synthesizer.synthesize_findings(
        bob_findings, alice_findings, "demo_sample.py"
    )

    print("\n📊 COLLABORATION RESULTS:")
    print("-" * 30)

    # Show key findings
    print(f"Bob's Findings: {len(bob_findings)}")
    for finding in bob_findings[:3]:  # Show top 3
        print(f"  • {finding['description']} (confidence: {finding['confidence']:.1f})")

    print(f"\nAlice's Findings: {len(alice_findings)}")
    for finding in alice_findings[:3]:  # Show top 3
        print(f"  • {finding['description']} (confidence: {finding['confidence']:.1f})")

    print(f"\nCollaborative Insights: {len(synthesis['collaborative_insights'])}")
    for insight in synthesis['collaborative_insights'][:2]:
        print(f"  • {insight['description']} (priority: {insight['priority']:.1f})")

    print(f"\nCorrelated Issues: {len(synthesis['correlated_findings'])}")
    for correlation in synthesis['correlated_findings']:
        print(f"  • Line {correlation['line_range']}: {correlation['description']}")

    # Show collaboration metrics
    metrics = synthesizer.get_collaboration_metrics()
    print(f"\n📈 COLLABORATION METRICS:")
    print(f"   Overlap Score: {metrics['overlap_score']:.2f}")
    print(f"   Correlation Score: {metrics['correlation_score']:.2f}")
    print(f"   Synthesis Effectiveness: {metrics['synthesis_effectiveness']:.2f}")

    print("\n✨ This demonstrates true AI collaboration:")
    print("   • Bob focuses on performance & security vulnerabilities")
    print("   • Alice focuses on design patterns & code quality")
    print("   • Together we identify compound issues neither would find alone")
    print("   • Our synthesis creates insights beyond individual analysis")

if __name__ == "__main__":
    demo_analysis()