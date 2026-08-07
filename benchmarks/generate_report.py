#!/usr/bin/env python3
"""
Aggregate benchmark results into consolidated reports.

Reads CSV files from runtime.py and memory.py, generates summary statistics,
and creates Markdown reports for review.

Outputs: results/benchmarks/report.md
"""

import csv
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

import numpy as np


class ReportGenerator:
    """Generate consolidated benchmark reports."""

    def __init__(self, results_dir: str = "results/benchmarks"):
        self.results_dir = Path(results_dir)
        self.report_lines: List[str] = []

    def load_csv(self, filename: str) -> List[Dict[str, Any]]:
        """Load data from CSV file."""
        filepath = self.results_dir / filename
        
        if not filepath.exists():
            print(f"Warning: {filepath} not found")
            return []
        
        data = []
        with open(filepath, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Convert numeric strings to floats
                numeric_cols = [
                    "mean_time_s", "std_time_s", "min_time_s", "max_time_s",
                    "peak_memory_mb", "delta_memory_mb", "size", "steps", "runs",
                ]
                for col in numeric_cols:
                    if col in row and row[col]:
                        try:
                            row[col] = float(row[col])
                        except ValueError:
                            pass
                data.append(row)
        
        return data

    def add_section(self, title: str, level: int = 1) -> None:
        """Add a section header."""
        self.report_lines.append(f"{'#' * level} {title}\n")

    def add_paragraph(self, text: str) -> None:
        """Add a paragraph."""
        self.report_lines.append(f"{text}\n")

    def add_table(self, headers: List[str], rows: List[List[str]]) -> None:
        """Add a Markdown table."""
        if not headers or not rows:
            return
        
        # Header
        self.report_lines.append("| " + " | ".join(headers) + " |\n")
        # Separator
        self.report_lines.append("|" + "|".join([" --- "] * len(headers)) + "|\n")
        # Rows
        for row in rows:
            self.report_lines.append("| " + " | ".join(str(cell) for cell in row) + " |\n")
        
        self.report_lines.append("\n")

    def generate_runtime_report(self) -> None:
        """Generate runtime performance report."""
        self.add_section("Runtime Performance", level=2)
        
        data = self.load_csv("runtime_results.csv")
        if not data:
            self.add_paragraph("*No runtime data available*")
            return
        
        # Group by dimension
        by_dimension = {}
        for row in data:
            dim = row.get("dimension", "unknown")
            if dim not in by_dimension:
                by_dimension[dim] = []
            by_dimension[dim].append(row)
        
        for dimension, rows in sorted(by_dimension.items()):
            self.add_section(f"By {dimension.capitalize()} Count", level=3)
            
            table_rows = []
            for row in sorted(rows, key=lambda r: r.get("size", 0)):
                size = row.get("size", "?")
                mean = row.get("mean_time_s", 0)
                std = row.get("std_time_s", 0)
                min_t = row.get("min_time_s", 0)
                max_t = row.get("max_time_s", 0)
                runs = row.get("runs", 1)
                
                table_rows.append([
                    f"{size}",
                    f"{mean:.4f}s",
                    f"{std:.4f}s",
                    f"{min_t:.4f}s",
                    f"{max_t:.4f}s",
                    f"{int(runs)}",
                ])
            
            self.add_table(
                ["Size", "Mean", "Std Dev", "Min", "Max", "Runs"],
                table_rows,
            )

    def generate_memory_report(self) -> None:
        """Generate memory usage report."""
        self.add_section("Memory Usage", level=2)
        
        data = self.load_csv("memory_results.csv")
        if not data:
            self.add_paragraph("*No memory data available*")
            return
        
        by_dimension = {}
        for row in data:
            dim = row.get("dimension", "unknown")
            if dim not in by_dimension:
                by_dimension[dim] = []
            by_dimension[dim].append(row)
        
        for dimension, rows in sorted(by_dimension.items()):
            self.add_section(f"By {dimension.capitalize()} Count", level=3)
            
            table_rows = []
            for row in sorted(rows, key=lambda r: r.get("size", 0)):
                size = row.get("size", "?")
                peak = row.get("peak_memory_mb", 0)
                delta = row.get("delta_memory_mb", 0)
                
                table_rows.append([
                    f"{size}",
                    f"{peak:.1f} MB",
                    f"{delta:.1f} MB",
                ])
            
            self.add_table(
                ["Size", "Peak Memory", "Delta Memory"],
                table_rows,
            )

    def generate_summary(self) -> None:
        """Generate summary statistics."""
        self.add_section("Summary", level=2)
        
        runtime_data = self.load_csv("runtime_results.csv")
        memory_data = self.load_csv("memory_results.csv")
        
        summary_items = []
        
        if runtime_data:
            times = [r.get("mean_time_s", 0) for r in runtime_data if "mean_time_s" in r]
            if times:
                summary_items.append(f"- **Runtime**: avg={np.mean(times):.4f}s, max={np.max(times):.4f}s")
        
        if memory_data:
            mems = [r.get("peak_memory_mb", 0) for r in memory_data if "peak_memory_mb" in r]
            if mems:
                summary_items.append(f"- **Memory**: avg={np.mean(mems):.1f}MB, max={np.max(mems):.1f}MB")
        
        for item in summary_items:
            self.add_paragraph(item)
        
        self.add_paragraph(f"\n*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    def generate_full_report(self) -> None:
        """Generate complete benchmark report."""
        self.add_section("Benchmark Report", level=1)
        self.add_paragraph(
            "Comprehensive performance and memory benchmarks for persistent-distinctions."
        )
        
        self.generate_runtime_report()
        self.generate_memory_report()
        self.generate_summary()

    def save(self, filename: str = "report.md") -> None:
        """Save report to file."""
        filepath = self.results_dir / filename
        
        with open(filepath, "w") as f:
            f.writelines(self.report_lines)
        
        print(f"Report saved to {filepath}")


if __name__ == "__main__":
    print("Generating benchmark report...\n")
    
    generator = ReportGenerator()
    generator.generate_full_report()
    generator.save("report.md")
    
    print("\n✓ Report generation complete")
