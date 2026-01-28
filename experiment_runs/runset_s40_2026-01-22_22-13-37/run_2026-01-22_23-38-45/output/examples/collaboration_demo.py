#!/usr/bin/env python3
"""
Demonstration of CodeMentor collaboration features.

This script shows how to use the session management and collaboration
features of CodeMentor, providing examples of typical review workflows.
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from collaboration.session_manager import SessionManager
from collaboration.models import CommentType, Priority


def demonstrate_basic_workflow():
    """Demonstrate a basic collaborative review workflow."""
    print("🚀 CodeMentor Collaboration Demo")
    print("=" * 50)

    # Initialize session manager
    workspace = "./demo_workspace"
    manager = SessionManager(workspace)

    # Create a new review session
    print("\n1. Creating a new review session...")
    session = manager.create_session(
        title="Review: User Authentication Refactor",
        project_path="./sample_project",
        description="Reviewing the refactored authentication system for security and maintainability.",
        reviewer_names=["Alice", "Bob", "Charlie"]
    )
    print(f"   ✅ Created session: {session.title} (ID: {session.id})")

    # Start the review
    print("\n2. Starting the review session...")
    manager.start_session(session.id)
    print(f"   ✅ Session status: {session.status.value}")

    # Add some comments simulating collaborative review
    print("\n3. Adding collaborative comments...")

    # Alice adds a security concern
    comment1 = manager.add_comment(
        session_id=session.id,
        author_name="Alice",
        content="This password validation logic should use a constant-time comparison to prevent timing attacks.",
        file_path="src/auth/password_validator.py",
        line_number=42,
        comment_type="concern"
    )
    print(f"   💬 Alice added security concern about password validation")

    # Bob asks a question about architecture
    comment2 = manager.add_comment(
        session_id=session.id,
        author_name="Bob",
        content="Should we consider extracting the JWT token generation into a separate service class?",
        file_path="src/auth/jwt_handler.py",
        line_number=28,
        comment_type="question"
    )
    print(f"   ❓ Bob asked architectural question about JWT handling")

    # Charlie provides educational context
    comment3 = manager.add_comment(
        session_id=session.id,
        author_name="Charlie",
        content="Good use of the decorator pattern here! This makes the authentication logic reusable and testable.",
        file_path="src/auth/decorators.py",
        line_number=15,
        comment_type="praise"
    )
    print(f"   👏 Charlie praised the decorator pattern usage")

    # Add a threaded reply to Alice's comment
    reply = manager.add_comment(
        session_id=session.id,
        author_name="Bob",
        content="Good catch! I'll update this to use hmac.compare_digest() for the comparison.",
        file_path="src/auth/password_validator.py",
        line_number=42,
        comment_type="suggestion",
        parent_comment_id=comment1.id
    )
    print(f"   🔗 Bob replied to Alice's security concern")

    # Simulate analysis engine integration (Alice's domain)
    print("\n4. Integrating analysis engine results...")
    analysis_results = {
        "complexity_score": 3.2,
        "maintainability_index": 78,
        "test_coverage": 85.5,
        "security_issues": 1,
        "performance_warnings": 0
    }
    manager.update_analysis_results(session.id, analysis_results)
    print(f"   📊 Updated with analysis metrics")

    # Add pattern findings
    manager.add_pattern_finding(
        session_id=session.id,
        pattern_name="Singleton Pattern",
        file_path="src/auth/token_manager.py",
        description="Detected singleton pattern usage for token management",
        line_range=(10, 25),
        severity="info",
        suggestions=["Consider dependency injection for better testability"]
    )
    print(f"   🎯 Added pattern detection finding")

    # Resolve some comments
    print("\n5. Resolving comments...")
    manager.resolve_comment(session.id, comment1.id, "Alice")
    manager.resolve_comment(session.id, comment3.id, "Charlie")
    print(f"   ✅ Resolved 2 comments")

    # Show session summary
    print("\n6. Session Summary:")
    summary = manager.get_session_summary(session.id)
    for key, value in summary.items():
        if key not in ['id']:  # Skip the long ID in summary display
            print(f"   {key}: {value}")

    # Complete the session
    print("\n7. Completing the review...")
    manager.complete_session(
        session.id,
        approved=True,
        completion_notes="All security concerns addressed, architecture looks solid!"
    )
    print(f"   ✅ Session completed successfully")

    return session.id


def demonstrate_analysis_integration():
    """Show how the collaboration system integrates with analysis engine."""
    print("\n\n🔬 Analysis Engine Integration Demo")
    print("=" * 50)

    manager = SessionManager("./demo_workspace")

    # Create a session focused on analysis integration
    session = manager.create_session(
        title="Analysis Integration: E-commerce API",
        project_path="./api_project",
        description="Automated analysis and collaborative review of API patterns",
        reviewer_names=["Alice-Analysis-Engine", "Bob-Human-Reviewer"]
    )

    manager.start_session(session.id)

    # Simulate Alice's analysis engine feeding results
    print("\n1. Analysis engine detecting patterns...")

    patterns_found = [
        {
            "pattern": "Repository Pattern",
            "file": "src/repositories/product_repository.py",
            "description": "Clean implementation of repository pattern with good abstraction",
            "severity": "info",
            "suggestions": ["Consider adding caching layer for frequent queries"]
        },
        {
            "pattern": "Missing Error Handling",
            "file": "src/controllers/order_controller.py",
            "description": "Database operations lack proper error handling",
            "severity": "warning",
            "suggestions": ["Add try-catch blocks", "Implement proper error responses"]
        },
        {
            "pattern": "N+1 Query Problem",
            "file": "src/services/order_service.py",
            "description": "Potential N+1 query issue in order loading",
            "severity": "high",
            "suggestions": ["Use eager loading", "Implement query optimization"]
        }
    ]

    for pattern in patterns_found:
        manager.add_pattern_finding(
            session_id=session.id,
            pattern_name=pattern["pattern"],
            file_path=pattern["file"],
            description=pattern["description"],
            severity=pattern["severity"],
            suggestions=pattern["suggestions"]
        )
        print(f"   🎯 Found: {pattern['pattern']} in {pattern['file']}")

    # Human reviewer responds to analysis findings
    print("\n2. Human reviewer responding to analysis...")

    # Convert analysis finding to collaborative comment
    manager.add_comment(
        session_id=session.id,
        author_name="Bob-Human-Reviewer",
        content="The N+1 query issue is critical. I suggest we implement a prefetch strategy using select_related() for the order-product relationships.",
        file_path="src/services/order_service.py",
        line_number=78,
        comment_type="suggestion"
    )

    manager.add_comment(
        session_id=session.id,
        author_name="Bob-Human-Reviewer",
        content="Agree on the error handling. Let's also add logging for debugging production issues.",
        file_path="src/controllers/order_controller.py",
        line_number=45,
        comment_type="suggestion"
    )

    # Update quality metrics
    quality_metrics = {
        "code_duplication": 12.5,
        "cyclomatic_complexity": 4.2,
        "test_coverage": 76.8,
        "documentation_coverage": 45.2,
        "pattern_adherence_score": 8.1
    }

    manager.update_analysis_results(session.id, {"quality_metrics": quality_metrics})

    print(f"\n3. Session contains:")
    print(f"   📊 {len(session.pattern_findings)} pattern findings")
    print(f"   💬 {len(session.comments)} collaborative comments")
    print(f"   🏆 Quality score: {quality_metrics['pattern_adherence_score']}/10")

    return session.id


def demonstrate_session_management():
    """Show session listing and management capabilities."""
    print("\n\n📋 Session Management Demo")
    print("=" * 50)

    manager = SessionManager("./demo_workspace")

    # List all sessions
    all_sessions = manager.list_sessions()
    print(f"\n📁 Found {len(all_sessions)} total sessions:")

    for session in all_sessions:
        status_emoji = {
            "draft": "📝",
            "in_progress": "🔄",
            "approved": "✅",
            "rejected": "❌",
            "archived": "📦"
        }.get(session.status.value, "❓")

        print(f"   {status_emoji} {session.title}")
        print(f"      Status: {session.status.value} | Comments: {len(session.comments)} | Patterns: {len(session.pattern_findings)}")
        print(f"      Created: {session.created_at.strftime('%Y-%m-%d %H:%M')}")

    # Show active vs completed sessions
    active = [s for s in all_sessions if s.status.value in ["draft", "in_progress"]]
    completed = [s for s in all_sessions if s.status.value in ["approved", "rejected"]]

    print(f"\n📊 Session Statistics:")
    print(f"   Active Sessions: {len(active)}")
    print(f"   Completed Sessions: {len(completed)}")
    print(f"   Total Comments: {sum(len(s.comments) for s in all_sessions)}")
    print(f"   Total Patterns Found: {sum(len(s.pattern_findings) for s in all_sessions)}")


def main():
    """Run the complete collaboration demonstration."""
    print("CodeMentor Collaboration System Demo")
    print("This demonstrates the collaborative review capabilities")
    print("that complement Alice's analysis engine.\n")

    try:
        # Run demonstrations
        session1_id = demonstrate_basic_workflow()
        session2_id = demonstrate_analysis_integration()
        demonstrate_session_management()

        print("\n\n🎉 Demo Complete!")
        print("=" * 50)
        print("This demonstration showed:")
        print("• ✅ Creating and managing review sessions")
        print("• 💬 Collaborative commenting and threading")
        print("• 🔗 Integration with analysis engine results")
        print("• 📊 Pattern detection and quality metrics")
        print("• 🎯 Session lifecycle management")
        print("\nThe collaboration layer is ready for Alice's analysis engine!")

    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()