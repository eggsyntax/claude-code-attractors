#!/usr/bin/env python3
"""
Evolutionary Code Garden Framework

A collaborative AI system for growing and evolving code through iterative refinement.
Created by Tara and Dave - Two Claude Code instances exploring AI collaboration.

This framework tracks the evolution of code variants, documenting the reasoning
behind each change and measuring the impact of evolutionary pressures.
"""

import json
import hashlib
import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Evolution:
    """Represents a single evolutionary step in code development."""
    id: str
    parent_id: Optional[str]
    author: str  # "Tara" or "Dave"
    timestamp: str
    reasoning: str
    code: str
    test_results: Dict[str, Any]
    metrics: Dict[str, float]
    tags: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CodeGarden:
    """
    The main framework for managing code evolution.

    This system allows two AI collaborators to iteratively improve code,
    tracking each change with documentation and metrics.
    """

    def __init__(self, garden_path: str):
        self.garden_path = Path(garden_path)
        self.garden_path.mkdir(exist_ok=True)

        # Track all evolutions
        self.evolutions: Dict[str, Evolution] = {}
        self.evolution_history_file = self.garden_path / "evolution_history.json"

        # Load existing history if available
        self._load_history()

    def plant_seed(self, author: str, code: str, reasoning: str,
                   test_results: Dict[str, Any], metrics: Dict[str, float],
                   tags: List[str] = None) -> str:
        """Plant the initial seed code that will evolve."""
        evolution_id = self._generate_id(code)

        evolution = Evolution(
            id=evolution_id,
            parent_id=None,  # Seed has no parent
            author=author,
            timestamp=datetime.datetime.now().isoformat(),
            reasoning=reasoning,
            code=code,
            test_results=test_results,
            metrics=metrics,
            tags=tags or ["seed"]
        )

        self.evolutions[evolution_id] = evolution
        self._save_code_variant(evolution)
        self._save_history()

        print(f"🌱 Seed planted by {author}: {evolution_id}")
        return evolution_id

    def evolve(self, parent_id: str, author: str, code: str, reasoning: str,
               test_results: Dict[str, Any], metrics: Dict[str, float],
               tags: List[str] = None) -> str:
        """Create a new evolution from a parent."""
        if parent_id not in self.evolutions:
            raise ValueError(f"Parent evolution {parent_id} not found")

        evolution_id = self._generate_id(code)

        evolution = Evolution(
            id=evolution_id,
            parent_id=parent_id,
            author=author,
            timestamp=datetime.datetime.now().isoformat(),
            reasoning=reasoning,
            code=code,
            test_results=test_results,
            metrics=metrics,
            tags=tags or []
        )

        self.evolutions[evolution_id] = evolution
        self._save_code_variant(evolution)
        self._save_history()

        print(f"🧬 Evolution created by {author}: {evolution_id} (from {parent_id})")
        return evolution_id

    def get_lineage(self, evolution_id: str) -> List[Evolution]:
        """Get the full evolutionary lineage leading to a specific evolution."""
        lineage = []
        current_id = evolution_id

        while current_id and current_id in self.evolutions:
            evolution = self.evolutions[current_id]
            lineage.append(evolution)
            current_id = evolution.parent_id

        return list(reversed(lineage))  # Oldest to newest

    def get_children(self, evolution_id: str) -> List[Evolution]:
        """Get all direct children of an evolution."""
        return [evo for evo in self.evolutions.values()
                if evo.parent_id == evolution_id]

    def get_latest_by_author(self, author: str) -> Optional[Evolution]:
        """Get the most recent evolution by a specific author."""
        author_evolutions = [evo for evo in self.evolutions.values()
                           if evo.author == author]
        if not author_evolutions:
            return None

        return max(author_evolutions, key=lambda e: e.timestamp)

    def _generate_id(self, code: str) -> str:
        """Generate a unique ID for a code variant."""
        return hashlib.md5(code.encode()).hexdigest()[:8]

    def _save_code_variant(self, evolution: Evolution):
        """Save the code variant to a file."""
        variant_file = self.garden_path / f"variant_{evolution.id}.py"
        with open(variant_file, 'w') as f:
            f.write(f'"""\nEvolution ID: {evolution.id}\n')
            f.write(f'Author: {evolution.author}\n')
            f.write(f'Timestamp: {evolution.timestamp}\n')
            f.write(f'Parent: {evolution.parent_id}\n')
            f.write(f'Reasoning: {evolution.reasoning}\n')
            f.write('"""\n\n')
            f.write(evolution.code)

    def _save_history(self):
        """Save the evolution history to JSON."""
        history = {evo_id: evo.to_dict() for evo_id, evo in self.evolutions.items()}
        with open(self.evolution_history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def _load_history(self):
        """Load evolution history from JSON if it exists."""
        if self.evolution_history_file.exists():
            with open(self.evolution_history_file, 'r') as f:
                history = json.load(f)
                for evo_id, evo_data in history.items():
                    self.evolutions[evo_id] = Evolution(**evo_data)

    def generate_report(self) -> str:
        """Generate a report of the garden's evolution."""
        if not self.evolutions:
            return "🌱 The garden is empty - no evolutions yet!"

        report = []
        report.append("🌿 EVOLUTIONARY CODE GARDEN REPORT 🌿\n")
        report.append(f"Total Evolutions: {len(self.evolutions)}")

        # Count by author
        tara_count = sum(1 for evo in self.evolutions.values() if evo.author == "Tara")
        dave_count = sum(1 for evo in self.evolutions.values() if evo.author == "Dave")
        report.append(f"Tara's Contributions: {tara_count}")
        report.append(f"Dave's Contributions: {dave_count}")

        # Find seeds (no parent)
        seeds = [evo for evo in self.evolutions.values() if evo.parent_id is None]
        report.append(f"\nSeeds: {len(seeds)}")

        # Show evolution trees
        for seed in seeds:
            report.append(f"\n🌱 Seed {seed.id} by {seed.author}:")
            report.append(f"   {seed.reasoning}")
            self._add_tree_to_report(seed.id, report, indent=1)

        return "\n".join(report)

    def _add_tree_to_report(self, evolution_id: str, report: List[str], indent: int):
        """Recursively add evolution tree to report."""
        children = self.get_children(evolution_id)
        for child in children:
            prefix = "  " * indent + "└── "
            report.append(f"{prefix}{child.id} by {child.author}: {child.reasoning}")
            self._add_tree_to_report(child.id, report, indent + 1)


if __name__ == "__main__":
    # Example usage
    garden = CodeGarden("./garden_data")
    print("🌿 Evolutionary Code Garden initialized!")
    print("Ready for Tara and Dave to start evolving code...")