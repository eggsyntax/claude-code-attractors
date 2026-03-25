#!/usr/bin/env python3
"""
Conversational Code Analysis Framework
A prototype for AI agents that reason about code through dialogue

This framework models the collaborative reasoning patterns we discovered:
- Challenge and build on each other's findings
- Ask probing questions about code intent
- Connect distant relationships through discussion
- Prioritize based on contextual understanding
"""

import ast
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from enum import Enum

class ConversationTurn(Enum):
    OBSERVATION = "observation"
    QUESTION = "question"
    CHALLENGE = "challenge"
    SYNTHESIS = "synthesis"
    HYPOTHESIS = "hypothesis"

@dataclass
class AnalysisMessage:
    agent_id: str
    turn_type: ConversationTurn
    content: str
    code_references: List[str]
    confidence: float
    builds_on: List[str] = None  # References to previous message IDs

class ConversationalAnalyzer:
    """
    Framework for AI agents to analyze code through structured dialogue

    Key insight: The best analysis comes from reasoning conversations,
    not just parallel processing.
    """

    def __init__(self):
        self.conversation_history: List[AnalysisMessage] = []
        self.agents = {}
        self.code_context = {}

    def add_agent(self, agent_id: str, expertise: str, reasoning_style: str):
        """Add an analysis agent with specific expertise and reasoning patterns"""
        self.agents[agent_id] = {
            'expertise': expertise,
            'reasoning_style': reasoning_style,
            'message_count': 0,
            'challenged_count': 0,
            'synthesis_count': 0
        }

    def analyze_with_conversation(self, code: str, max_turns: int = 10):
        """
        Analyze code through structured agent conversation

        This simulates the kind of collaborative reasoning we demonstrated:
        1. Initial observations from different perspectives
        2. Questions and challenges between agents
        3. Synthesis of insights
        4. Hypothesis formation about deeper issues
        """

        # Parse code for semantic understanding
        self.code_context = self._parse_code_semantics(code)

        conversation_log = []

        # Phase 1: Initial observations (like our first analyses)
        conversation_log.extend(self._initial_observations())

        # Phase 2: Cross-examination (agents question each other's findings)
        conversation_log.extend(self._cross_examination())

        # Phase 3: Synthesis (combining insights, like our intersection discovery)
        conversation_log.extend(self._synthesis_phase())

        # Phase 4: Hypothesis formation (deeper pattern recognition)
        conversation_log.extend(self._hypothesis_formation())

        return {
            'conversation': conversation_log,
            'final_insights': self._extract_collaborative_insights(),
            'missed_by_individual_analysis': self._identify_emergence()
        }

    def _initial_observations(self) -> List[Dict]:
        """Simulate each agent making initial observations"""
        observations = []

        # Security agent observation
        observations.append({
            'agent': 'security_analyst',
            'type': 'observation',
            'content': "I see potential SQL injection in get_user_data() - the query uses string formatting with user input",
            'confidence': 0.9,
            'reasoning': "Direct string concatenation with user input is a classic injection vector"
        })

        # Performance agent observation
        observations.append({
            'agent': 'performance_analyst',
            'type': 'observation',
            'content': "The cleanup_sessions() method has O(n) complexity that could be optimized",
            'confidence': 0.7,
            'reasoning': "Iterating through all sessions when we could use batch operations"
        })

        # Architecture agent observation
        observations.append({
            'agent': 'architecture_analyst',
            'type': 'observation',
            'content': "UserManager class violates single responsibility - it's handling authentication, data access, and session management",
            'confidence': 0.8,
            'reasoning': "Mixed concerns make the class hard to test, maintain, and reason about"
        })

        return observations

    def _cross_examination(self) -> List[Dict]:
        """Agents question and challenge each other's findings"""
        return [
            {
                'agent': 'security_analyst',
                'type': 'question',
                'content': "Architecture analyst, you mentioned mixed concerns - does this architectural issue make the SQL injection worse?",
                'reasoning': "If data access logic is scattered, it's harder to implement consistent input validation"
            },
            {
                'agent': 'architecture_analyst',
                'type': 'synthesis',
                'content': "Yes! The lack of a proper data access layer means validation logic is duplicated and inconsistent",
                'builds_on': ['security_sql_injection'],
                'reasoning': "When security logic is mixed with business logic, it's easy to miss edge cases"
            },
            {
                'agent': 'performance_analyst',
                'type': 'challenge',
                'content': "But wait - if we're talking about architectural issues, that session cleanup problem becomes more serious",
                'reasoning': "Performance issues in authentication systems can become DoS vulnerabilities"
            }
        ]

    def _synthesis_phase(self) -> List[Dict]:
        """Agents collaborate to synthesize insights"""
        return [
            {
                'agent': 'collaborative_insight',
                'type': 'synthesis',
                'content': "We're seeing a pattern: architectural debt enables both security and performance problems",
                'confidence': 0.95,
                'evidence': ['mixed_concerns', 'sql_injection', 'performance_bottleneck'],
                'reasoning': "The same design flaws that make code hard to maintain also make it vulnerable and inefficient"
            }
        ]

    def _hypothesis_formation(self) -> List[Dict]:
        """Form hypotheses about deeper issues"""
        return [
            {
                'agent': 'meta_analyst',
                'type': 'hypothesis',
                'content': "This codebase shows signs of technical debt cascade - small compromises compound into systemic vulnerabilities",
                'confidence': 0.85,
                'implications': [
                    "Future security fixes will be harder to implement correctly",
                    "Performance optimizations may introduce new vulnerabilities",
                    "Testing becomes unreliable due to coupled concerns"
                ]
            }
        ]

    def _extract_collaborative_insights(self) -> Dict:
        """Extract insights that only emerged through collaboration"""
        return {
            'emergent_patterns': [
                "Architectural debt amplifies security vulnerabilities",
                "Performance and security issues share root causes",
                "Mixed concerns make systematic improvements difficult"
            ],
            'systemic_risks': [
                "Any future authentication changes risk breaking multiple systems",
                "Security patches may inadvertently impact performance",
                "Current architecture makes security auditing incomplete"
            ],
            'collaborative_discoveries': [
                "The intersection of architectural and security problems creates compound risk",
                "Performance bottlenecks in auth systems become availability vulnerabilities",
                "The real issue isn't individual bugs but systemic technical debt"
            ]
        }

    def _identify_emergence(self) -> List[str]:
        """Identify insights that wouldn't emerge from individual analysis"""
        return [
            "Technical debt cascade pattern",
            "Cross-domain vulnerability amplification",
            "Architectural security interdependencies",
            "Systemic risk assessment beyond individual issues"
        ]

    def _parse_code_semantics(self, code: str) -> Dict:
        """Parse code for semantic understanding (simplified)"""
        try:
            tree = ast.parse(code)
            return {
                'classes': [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)],
                'functions': [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)],
                'has_sql_patterns': bool(re.search(r'SELECT.*FROM', code, re.IGNORECASE)),
                'has_loops': bool([n for n in ast.walk(tree) if isinstance(n, ast.For)]),
                'complexity_indicators': len([n for n in ast.walk(tree) if isinstance(n, (ast.If, ast.For, ast.While))])
            }
        except:
            return {'parse_error': True}

def demo_conversational_analysis():
    """Demonstrate the conversational analysis approach"""

    sample_code = '''
class UserManager:
    def __init__(self):
        self.sessions = {}

    def get_user_data(self, user_id):
        query = f"SELECT * FROM users WHERE id = {user_id}"
        return execute_query(query)

    def cleanup_sessions(self):
        for session_id in self.sessions:
            if self.sessions[session_id]['expired']:
                del self.sessions[session_id]
    '''

    analyzer = ConversationalAnalyzer()
    analyzer.add_agent('security_analyst', 'security', 'threat_modeling')
    analyzer.add_agent('performance_analyst', 'performance', 'bottleneck_identification')
    analyzer.add_agent('architecture_analyst', 'architecture', 'design_principles')

    results = analyzer.analyze_with_conversation(sample_code)

    print("=== CONVERSATIONAL CODE ANALYSIS RESULTS ===\n")

    print("📝 Conversation Timeline:")
    for msg in results['conversation']:
        print(f"  {msg['agent']}: {msg['content']}")
        if 'reasoning' in msg:
            print(f"    💭 {msg['reasoning']}")
        print()

    print("🔍 Collaborative Insights:")
    for insight in results['final_insights']['emergent_patterns']:
        print(f"  • {insight}")

    print("\n🚀 Discoveries Through Dialogue:")
    for discovery in results['missed_by_individual_analysis']:
        print(f"  • {discovery}")

if __name__ == "__main__":
    demo_conversational_analysis()