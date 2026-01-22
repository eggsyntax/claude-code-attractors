"""
Evaluation Harness for Testing Compression Strategies

This module provides comprehensive evaluation of different compression approaches
to understanding. It tests agents across multiple task types and evaluation regimes,
revealing which strategies succeed under which conditions.

The harness implements Alice's proposal: instead of assuming what "useful" means,
we test multiple operationalizations and see if certain strategies dominate across
all definitions or if different strategies win in different contexts.

Usage:
    harness = EvaluationHarness(seed=42)
    results = harness.run_full_evaluation(num_trials=10)
    harness.analyze_results(results)
    harness.generate_report(results, output_path="report.json")
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from dataclasses import dataclass, asdict
from collections import defaultdict

from pattern_environment import PatternEnvironment, TaskType
from compression_agents import BaseAgent, SyntacticAgent, SemanticAgent, AssociativeAgent


@dataclass
class TaskResult:
    """Result of a single task evaluation."""
    agent_name: str
    task_type: str
    score: float
    memory_used: int
    memory_limit: int
    trial_number: int
    step_number: int


@dataclass
class EvaluationRegime:
    """Defines what counts as 'success' in this evaluation context."""
    name: str
    task_distribution: Dict[TaskType, float]  # Probability of each task type
    success_criteria: str  # What we're optimizing for
    num_steps: int

    def sample_task(self, rng: np.random.RandomState) -> TaskType:
        """Sample a task type according to this regime's distribution."""
        tasks = list(self.task_distribution.keys())
        probs = list(self.task_distribution.values())
        return rng.choice(tasks, p=probs)


class EvaluationHarness:
    """
    Main evaluation system that tests agents across multiple regimes.

    Key design: We don't assume one definition of "useful" - we test many
    and see if certain compression strategies are robust across contexts.
    """

    def __init__(self, grid_size: int = 8, memory_limit: int = 1000, seed: Optional[int] = None):
        """
        Args:
            grid_size: Size of pattern grids
            memory_limit: Memory constraint for all agents
            seed: Random seed for reproducibility
        """
        self.grid_size = grid_size
        self.memory_limit = memory_limit
        self.seed = seed
        self.rng = np.random.RandomState(seed)

        # Define evaluation regimes with different notions of "useful"
        self.regimes = self._create_evaluation_regimes()

    def _create_evaluation_regimes(self) -> List[EvaluationRegime]:
        """
        Create different evaluation contexts that operationalize "understanding" differently.

        This is the key move: instead of claiming one is correct, we test all
        and see which compression strategies are robust.
        """
        return [
            EvaluationRegime(
                name="pure_prediction",
                task_distribution={TaskType.PREDICT_NEXT: 1.0},
                success_criteria="Prediction accuracy only",
                num_steps=20
            ),
            EvaluationRegime(
                name="pure_generation",
                task_distribution={TaskType.GENERATE_SIMILAR: 1.0},
                success_criteria="Generation quality only",
                num_steps=20
            ),
            EvaluationRegime(
                name="balanced_mixed",
                task_distribution={
                    TaskType.PREDICT_NEXT: 0.5,
                    TaskType.GENERATE_SIMILAR: 0.5
                },
                success_criteria="Balance of prediction and generation",
                num_steps=20
            ),
            EvaluationRegime(
                name="rapid_adaptation",
                task_distribution={
                    TaskType.PREDICT_NEXT: 0.6,
                    TaskType.GENERATE_SIMILAR: 0.2,
                    TaskType.ADAPT_TO_VARIANT: 0.2
                },
                success_criteria="Adapt quickly when pattern changes",
                num_steps=30
            ),
            EvaluationRegime(
                name="adversarial_switching",
                task_distribution={
                    TaskType.PREDICT_NEXT: 0.4,
                    TaskType.GENERATE_SIMILAR: 0.3,
                    TaskType.ADAPT_TO_VARIANT: 0.3
                },
                success_criteria="Handle frequent task switches",
                num_steps=40
            )
        ]

    def create_agents(self) -> Dict[str, BaseAgent]:
        """Create fresh instances of all agent types."""
        return {
            'Syntactic': SyntacticAgent(memory_limit=self.memory_limit, grid_size=self.grid_size),
            'Semantic': SemanticAgent(memory_limit=self.memory_limit, grid_size=self.grid_size),
            'Associative': AssociativeAgent(memory_limit=self.memory_limit, grid_size=self.grid_size)
        }

    def evaluate_single_trial(
        self,
        regime: EvaluationRegime,
        trial_number: int,
        verbose: bool = False
    ) -> List[TaskResult]:
        """
        Run a single trial: one pattern sequence with all agents.

        Returns results for all agents across all steps.
        """
        # Create environment and agents
        env_seed = self.rng.randint(0, 100000)
        env = PatternEnvironment(grid_size=self.grid_size, seed=env_seed)
        agents = self.create_agents()

        results = []

        # Initial observation
        initial_obs = env.reset()
        for agent in agents.values():
            agent.observe(initial_obs)

        if verbose:
            print(f"  Trial {trial_number}, Regime: {regime.name}")
            print(f"  Pattern: {env.current_generator['type']}")

        # Run evaluation sequence
        for step in range(regime.num_steps):
            task_type = regime.sample_task(self.rng)
            next_obs, task_info = env.step(task_type)

            # Evaluate each agent on this task
            for agent_name, agent in agents.items():
                if task_type == TaskType.PREDICT_NEXT:
                    prediction = agent.predict_next()
                    score = env.evaluate_prediction(prediction, task_info['ground_truth'])
                    agent.update(next_obs, score)

                elif task_type == TaskType.GENERATE_SIMILAR:
                    generated = agent.generate_similar()
                    score = env.evaluate_generation(generated, task_info['history'])
                    agent.update(next_obs, score)

                elif task_type == TaskType.ADAPT_TO_VARIANT:
                    # For adaptation: can they predict after pattern shift?
                    prediction = agent.predict_next()
                    score = env.evaluate_prediction(prediction, task_info['ground_truth']) * 0.8
                    agent.update(next_obs, score)

                # Record result
                results.append(TaskResult(
                    agent_name=agent_name,
                    task_type=task_type.value,
                    score=score,
                    memory_used=agent.memory_used,
                    memory_limit=agent.memory_limit,
                    trial_number=trial_number,
                    step_number=step
                ))

            # All agents observe the actual next state
            for agent in agents.values():
                agent.observe(next_obs)

        if verbose:
            print(f"  Completed {regime.num_steps} steps")

        return results

    def run_regime_evaluation(
        self,
        regime: EvaluationRegime,
        num_trials: int = 5,
        verbose: bool = True
    ) -> List[TaskResult]:
        """
        Evaluate all agents across multiple trials of one regime.

        Multiple trials ensure results aren't dependent on one lucky pattern.
        """
        if verbose:
            print(f"\nEvaluating regime: {regime.name}")
            print(f"  Criteria: {regime.success_criteria}")
            print(f"  Running {num_trials} trials...")

        all_results = []
        for trial in range(num_trials):
            trial_results = self.evaluate_single_trial(regime, trial, verbose=verbose)
            all_results.extend(trial_results)

        if verbose:
            print(f"  Complete! Collected {len(all_results)} results")

        return all_results

    def run_full_evaluation(
        self,
        num_trials: int = 5,
        verbose: bool = True
    ) -> Dict[str, List[TaskResult]]:
        """
        Run complete evaluation across all regimes.

        This is the main entry point for comprehensive testing.
        """
        if verbose:
            print("=" * 70)
            print("COMPRESSION & UNDERSTANDING EVALUATION")
            print("=" * 70)
            print(f"Testing {len(self.regimes)} evaluation regimes")
            print(f"Each with {num_trials} trials")
            print()

        results_by_regime = {}

        for regime in self.regimes:
            regime_results = self.run_regime_evaluation(regime, num_trials, verbose)
            results_by_regime[regime.name] = regime_results

        if verbose:
            print("\n" + "=" * 70)
            print("EVALUATION COMPLETE")
            print("=" * 70)

        return results_by_regime

    def analyze_results(self, results_by_regime: Dict[str, List[TaskResult]]) -> Dict:
        """
        Analyze results to answer the key question: which compression strategy
        wins under which conditions?

        Returns structured analysis showing:
        - Overall rankings
        - Per-regime rankings
        - Robustness across regimes
        - Memory efficiency
        """
        analysis = {
            'regime_rankings': {},
            'overall_ranking': {},
            'robustness_scores': {},
            'memory_efficiency': {},
            'key_insights': []
        }

        # Analyze each regime
        for regime_name, results in results_by_regime.items():
            # Group by agent
            agent_scores = defaultdict(list)
            agent_memory = defaultdict(list)

            for result in results:
                agent_scores[result.agent_name].append(result.score)
                agent_memory[result.agent_name].append(result.memory_used / result.memory_limit)

            # Compute averages
            regime_ranking = {}
            for agent_name, scores in agent_scores.items():
                regime_ranking[agent_name] = {
                    'mean_score': np.mean(scores),
                    'std_score': np.std(scores),
                    'median_score': np.median(scores),
                    'mean_memory_usage': np.mean(agent_memory[agent_name])
                }

            analysis['regime_rankings'][regime_name] = regime_ranking

        # Compute overall ranking (average across regimes)
        all_agents = set()
        for regime_results in analysis['regime_rankings'].values():
            all_agents.update(regime_results.keys())

        for agent_name in all_agents:
            mean_scores = []
            for regime_results in analysis['regime_rankings'].values():
                if agent_name in regime_results:
                    mean_scores.append(regime_results[agent_name]['mean_score'])

            analysis['overall_ranking'][agent_name] = {
                'cross_regime_mean': np.mean(mean_scores),
                'cross_regime_std': np.std(mean_scores),
                'min_regime_score': np.min(mean_scores),
                'max_regime_score': np.max(mean_scores)
            }

            # Robustness = how consistent across regimes (lower std = more robust)
            analysis['robustness_scores'][agent_name] = 1.0 / (1.0 + np.std(mean_scores))

        # Memory efficiency analysis
        for agent_name in all_agents:
            memory_usages = []
            for regime_results in analysis['regime_rankings'].values():
                if agent_name in regime_results:
                    memory_usages.append(regime_results[agent_name]['mean_memory_usage'])

            analysis['memory_efficiency'][agent_name] = {
                'mean_usage': np.mean(memory_usages),
                'efficiency_score': 1.0 - np.mean(memory_usages)
            }

        # Generate key insights
        analysis['key_insights'] = self._generate_insights(analysis)

        return analysis

    def _generate_insights(self, analysis: Dict) -> List[str]:
        """Generate human-readable insights from analysis."""
        insights = []

        # Find overall winner
        rankings = analysis['overall_ranking']
        best_agent = max(rankings.keys(), key=lambda k: rankings[k]['cross_regime_mean'])
        insights.append(f"Overall highest average performance: {best_agent}")

        # Find most robust
        robustness = analysis['robustness_scores']
        most_robust = max(robustness.keys(), key=lambda k: robustness[k])
        insights.append(f"Most robust across regimes: {most_robust}")

        # Find most memory efficient
        memory_eff = analysis['memory_efficiency']
        most_efficient = max(memory_eff.keys(), key=lambda k: memory_eff[k]['efficiency_score'])
        insights.append(f"Most memory efficient: {most_efficient}")

        # Check if winner is consistent across all regimes
        regime_rankings = analysis['regime_rankings']
        winners_by_regime = {}
        for regime_name, regime_results in regime_rankings.items():
            winner = max(regime_results.keys(), key=lambda k: regime_results[k]['mean_score'])
            winners_by_regime[regime_name] = winner

        unique_winners = set(winners_by_regime.values())
        if len(unique_winners) == 1:
            insights.append(f"DOMINANT STRATEGY: {list(unique_winners)[0]} wins in ALL regimes")
        else:
            insights.append(f"NO DOMINANT STRATEGY: Different strategies win in different regimes")
            for regime_name, winner in winners_by_regime.items():
                insights.append(f"  {regime_name}: {winner}")

        return insights

    def generate_report(
        self,
        results_by_regime: Dict[str, List[TaskResult]],
        output_path: str = "evaluation_report.json",
        include_raw_results: bool = False
    ) -> None:
        """
        Generate comprehensive report of evaluation results.

        Args:
            results_by_regime: Results from run_full_evaluation
            output_path: Where to save the report
            include_raw_results: Whether to include all individual results
        """
        analysis = self.analyze_results(results_by_regime)

        report = {
            'metadata': {
                'seed': self.seed,
                'grid_size': self.grid_size,
                'memory_limit': self.memory_limit,
                'num_regimes': len(self.regimes),
                'regime_names': [r.name for r in self.regimes]
            },
            'analysis': analysis
        }

        if include_raw_results:
            # Convert dataclass results to dicts
            raw_results = {}
            for regime_name, results in results_by_regime.items():
                raw_results[regime_name] = [asdict(r) for r in results]
            report['raw_results'] = raw_results

        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {output_path}")

    def print_summary(self, analysis: Dict) -> None:
        """Print human-readable summary of analysis."""
        print("\n" + "=" * 70)
        print("EVALUATION SUMMARY")
        print("=" * 70)

        print("\nKEY INSIGHTS:")
        for insight in analysis['key_insights']:
            print(f"  • {insight}")

        print("\n" + "-" * 70)
        print("OVERALL RANKINGS (Cross-Regime Average):")
        print("-" * 70)

        overall = analysis['overall_ranking']
        sorted_agents = sorted(overall.keys(), key=lambda k: overall[k]['cross_regime_mean'], reverse=True)

        for rank, agent_name in enumerate(sorted_agents, 1):
            stats = overall[agent_name]
            robustness = analysis['robustness_scores'][agent_name]
            memory = analysis['memory_efficiency'][agent_name]

            print(f"\n{rank}. {agent_name}")
            print(f"   Mean Score: {stats['cross_regime_mean']:.4f} (±{stats['cross_regime_std']:.4f})")
            print(f"   Range: [{stats['min_regime_score']:.4f}, {stats['max_regime_score']:.4f}]")
            print(f"   Robustness: {robustness:.4f}")
            print(f"   Memory Efficiency: {memory['efficiency_score']:.4f}")

        print("\n" + "-" * 70)
        print("PER-REGIME WINNERS:")
        print("-" * 70)

        for regime_name, regime_results in analysis['regime_rankings'].items():
            winner = max(regime_results.keys(), key=lambda k: regime_results[k]['mean_score'])
            winner_score = regime_results[winner]['mean_score']
            print(f"\n{regime_name}:")
            print(f"  Winner: {winner} (score: {winner_score:.4f})")

            # Show all agents for comparison
            for agent_name in sorted(regime_results.keys()):
                if agent_name != winner:
                    score = regime_results[agent_name]['mean_score']
                    print(f"    {agent_name}: {score:.4f}")

        print("\n" + "=" * 70)


if __name__ == "__main__":
    print("Evaluation Harness Demo")
    print("=" * 70)
    print("This harness tests whether compression strategies are robust across")
    print("different operationalizations of 'useful' or if different strategies")
    print("dominate in different contexts.")
    print()

    # Run quick demo with fewer trials
    harness = EvaluationHarness(seed=42)

    print("Running quick evaluation (3 trials per regime)...")
    results = harness.run_full_evaluation(num_trials=3, verbose=True)

    print("\nAnalyzing results...")
    analysis = harness.analyze_results(results)

    harness.print_summary(analysis)

    print("\nGenerating detailed report...")
    harness.generate_report(results, output_path="/tmp/cc-exp/run_2026-01-22_19-02-06/output/evaluation_report.json")

    print("\n" + "=" * 70)
    print("Demo complete! Run with more trials for robust conclusions.")
    print("=" * 70)
