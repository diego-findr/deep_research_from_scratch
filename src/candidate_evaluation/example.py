"""
Example script demonstrating the multi-agent candidate evaluation system.

This script loads enriched candidate and job data, runs the evaluation graph,
and displays the results including agent evaluations, debate transcript,
questions, and final consensus decision.

Usage:
    python example.py -c enriched_candidate.json -o enriched_job.json
    python example.py -c tests/candidates/outputs/enriched_noelia.json -o tests/jobs/outputs/enriched_veterinario_offer.json
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from candidate_evaluation.evaluation_agent import evaluate_candidate


console = Console()


def load_data(candidate_path: str, job_path: str):
    """Load enriched candidate and job data from specified paths.
    
    Args:
        candidate_path: Path to enriched candidate JSON file
        job_path: Path to enriched job offer JSON file
    
    Returns:
        Tuple of (enriched_candidate, enriched_job)
    """
    # Resolve paths relative to project root
    project_root = Path(__file__).parent.parent.parent
    
    # If path is relative, resolve it from project root
    candidate_file = Path(candidate_path)
    if not candidate_file.is_absolute():
        candidate_file = project_root / candidate_path
    
    job_file = Path(job_path)
    if not job_file.is_absolute():
        job_file = project_root / job_path
    
    # Load files
    with open(candidate_file, 'r', encoding='utf-8') as f:
        enriched_candidate = json.load(f)
    
    with open(job_file, 'r', encoding='utf-8') as f:
        enriched_job = json.load(f)
    
    return enriched_candidate, enriched_job


def display_agent_evaluation(evaluation: dict):
    """Display a single agent evaluation in a formatted panel."""
    agent_name = evaluation['agent_name'].replace('_', ' ').title()
    
    # Create table for evaluation details
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    
    table.add_row("Score", f"{evaluation['score']:.2f} / 1.0")
    table.add_row("Recommendation", f"[bold]{evaluation['recommendation']}[/bold]")
    table.add_row("Focus", evaluation['evaluation_focus'])
    table.add_row("Sector Expertise", evaluation['agent_sector_expertise'])
    
    panel_content = f"{table}\n\n"
    panel_content += f"[bold green]Strengths:[/bold green]\n"
    for strength in evaluation['strengths']:
        panel_content += f"  ✓ {strength}\n"
    
    panel_content += f"\n[bold red]Weaknesses:[/bold red]\n"
    for weakness in evaluation['weaknesses']:
        panel_content += f"  ✗ {weakness}\n"
    
    if evaluation.get('concerns'):
        panel_content += f"\n[bold yellow]Concerns for Debate:[/bold yellow]\n"
        for concern in evaluation['concerns']:
            panel_content += f"  ⚠ {concern}\n"
    
    return Panel(
        panel_content,
        title=f"🤖 {agent_name}",
        border_style="blue",
    )


def display_debate_messages(messages: list):
    """Display debate messages in a tree structure."""
    tree = Tree("💬 [bold]Agent Debate Transcript[/bold]")
    
    for i, msg in enumerate(messages, 1):
        from_agent = msg['from_agent'].replace('_', ' ').title()
        content_preview = msg['content'][:200] + "..." if len(msg['content']) > 200 else msg['content']
        
        branch = tree.add(f"[cyan]Message {i}[/cyan] from {from_agent}")
        branch.add(f"[dim]{content_preview}[/dim]")
    
    return tree


def display_questions(questions: list):
    """Display generated questions."""
    table = Table(title="❓ Specialized Questions Generated", show_lines=True)
    table.add_column("Agent", style="cyan")
    table.add_column("Priority", style="yellow")
    table.add_column("Question", style="white")
    
    for q in questions:
        agent_name = q['agent_name'].replace('_', ' ').title()
        priority = q['priority'].upper()
        question_preview = q['question_text'][:150] + "..." if len(q['question_text']) > 150 else q['question_text']
        
        table.add_row(agent_name, priority, question_preview)
    
    return table


def display_consensus(decision: dict):
    """Display final consensus decision."""
    # Decision header
    decision_icon = "✅" if decision['liked'] else "❌"
    decision_text = "RECOMMEND TO PROCEED" if decision['liked'] else "DO NOT RECOMMEND"
    
    content = f"[bold]{decision_icon} {decision_text}[/bold]\n\n"
    
    # Metrics table
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    
    table.add_row("Overall Score", f"{decision['overall_score']:.2f} / 1.0")
    table.add_row("Decision Confidence", f"{decision['decision_confidence']:.2f} / 1.0")
    
    content += f"{table}\n\n"
    
    # Primary reasons
    content += "[bold]Primary Reasons:[/bold]\n"
    for i, reason in enumerate(decision['primary_reasons'], 1):
        content += f"  {i}. {reason}\n"
    
    # Key strengths
    content += "\n[bold green]Key Strengths:[/bold green]\n"
    for strength in decision['key_strengths']:
        content += f"  ✓ {strength}\n"
    
    # Key concerns
    content += "\n[bold red]Key Concerns:[/bold red]\n"
    for concern in decision['key_concerns']:
        content += f"  ✗ {concern}\n"
    
    # Compatibility breakdown
    content += "\n[bold]Compatibility Breakdown:[/bold]\n"
    for item in decision['compatibility_breakdown']:
        dimension = item['dimension'].replace('_', ' ').title()
        score = item['score']
        content += f"  • {dimension}: {score:.2f}\n"
    
    # Suggested next steps
    if decision.get('suggested_next_steps'):
        content += "\n[bold]Suggested Next Steps:[/bold]\n"
        for step in decision['suggested_next_steps']:
            content += f"  → {step}\n"
    
    return Panel(
        content,
        title="🎯 Final Consensus Decision",
        border_style="green" if decision['liked'] else "red",
    )


def save_results(result: dict, candidate_name: str, job_title: str, output_dir: Path):
    """Save evaluation results to JSON file with organized structure.
    
    Args:
        result: Evaluation results dictionary
        candidate_name: Name of the candidate
        job_title: Title of the job
        output_dir: Directory to save results
    """
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean names for filename (remove invalid characters)
    import re
    candidate_slug = re.sub(r'[^\w\s-]', '', candidate_name.lower())[:20].replace(" ", "_")
    job_slug = re.sub(r'[^\w\s-]', '', job_title.lower())[:30].replace(" ", "_")
    filename = f"evaluation_{candidate_slug}_vs_{job_slug}_{timestamp}.json"
    
    output_path = output_dir / filename
    
    # Extract only evaluation results (exclude enriched_candidate and enriched_job)
    evaluation_only = {
        "agent_evaluations": result.get("agent_evaluations", []),
        "debate_messages": result.get("debate_messages", []),
        "questions_asked": result.get("questions_asked", []),
        "consensus_decision": result.get("consensus_decision", {}),
        "reasoning_log": result.get("reasoning_log", []),
    }
    
    # Save with metadata
    output_data = {
        "evaluation_metadata": {
            "candidate_name": candidate_name,
            "job_title": job_title,
            "timestamp": datetime.now().isoformat(),
            "evaluation_version": "1.0",
        },
        "evaluation_results": evaluation_only,
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    console.print(f"\n[green]✓ Results saved to:[/green] {output_path}")
    return output_path


def main():
    """Run the multi-agent candidate evaluation example."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Multi-Agent Candidate Evaluation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use default test data
  python example.py
  
  # Specify custom candidate and job offer
  python example.py -c tests/candidates/outputs/enriched_noelia.json -o tests/jobs/outputs/enriched_veterinario_offer.json
  
  # Use absolute paths
  python example.py -c /path/to/candidate.json -o /path/to/offer.json
        """
    )
    
    parser.add_argument(
        '-c', '--candidate',
        type=str,
        default="tests/candidates/outputs/enriched_noelia.json",
        help="Path to enriched candidate JSON file (default: tests/candidates/outputs/enriched_noelia.json)"
    )
    
    parser.add_argument(
        '-o', '--offer',
        type=str,
        default="tests/jobs/outputs/enriched_veterinario_offer.json",
        help="Path to enriched job offer JSON file (default: tests/jobs/outputs/enriched_veterinario_offer.json)"
    )
    
    parser.add_argument(
        '--output-dir',
        type=str,
        default="tests/evaluation_results",
        help="Directory to save evaluation results (default: tests/evaluation_results)"
    )
    
    parser.add_argument(
        '--max-debate-rounds',
        type=int,
        default=2,
        help="Maximum number of debate rounds (default: 2)"
    )
    
    args = parser.parse_args()
    
    console.rule("[bold blue]Multi-Agent Candidate Evaluation System[/bold blue]")
    
    # Load data
    console.print("\n[cyan]Loading data...[/cyan]")
    console.print(f"  Candidate: {args.candidate}")
    console.print(f"  Job Offer: {args.offer}")
    
    try:
        enriched_candidate, enriched_job = load_data(args.candidate, args.offer)
    except FileNotFoundError as e:
        console.print(f"\n[red]✗ Error:[/red] File not found - {e}")
        console.print("[yellow]Tip:[/yellow] Use -c and -o flags to specify candidate and job offer files")
        return 1
    except json.JSONDecodeError as e:
        console.print(f"\n[red]✗ Error:[/red] Invalid JSON - {e}")
        return 1
    
    candidate_name = enriched_candidate['identity']['full_name']
    
    # Handle both old and new job enrichment formats
    if 'raw_job_posting' in enriched_job:
        job_title = enriched_job['raw_job_posting']['job_title']
    elif 'identity' in enriched_job:
        job_title = enriched_job['identity']['title']
    else:
        job_title = "Unknown Position"
    
    console.print(f"\n  Candidate Name: [bold]{candidate_name}[/bold]")
    console.print(f"  Job Title: [bold]{job_title}[/bold]\n")
    
    # Run evaluation
    console.rule("[bold]Running Multi-Agent Evaluation[/bold]")
    
    result = evaluate_candidate(
        enriched_candidate=enriched_candidate,
        enriched_job=enriched_job,
        max_debate_rounds=args.max_debate_rounds,
    )
    
    # Display results
    console.rule("[bold]Evaluation Results[/bold]")
    
    # Agent evaluations
    console.print("\n[bold]Individual Agent Evaluations:[/bold]\n")
    for evaluation in result['agent_evaluations']:
        console.print(display_agent_evaluation(evaluation))
        console.print()
    
    # Debate transcript
    if result.get('debate_messages'):
        console.print("\n")
        console.print(display_debate_messages(result['debate_messages']))
        console.print()
    
    # Questions
    if result.get('questions_asked'):
        console.print("\n")
        console.print(display_questions(result['questions_asked']))
        console.print()
    
    # Final consensus
    console.print("\n")
    console.print(display_consensus(result['consensus_decision']))
    
    # Save results
    output_dir = Path(__file__).parent.parent.parent / args.output_dir
    save_results(result, candidate_name, job_title, output_dir)
    
    console.rule("[bold green]Evaluation Complete[/bold green]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
