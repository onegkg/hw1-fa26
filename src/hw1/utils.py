"""Utility functions for sentiment analysis."""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import click
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_bar(data, title=None, xlabel=None, ylabel=None):
    """Create a bar plot from a dictionary.

    Args:
        data: Dictionary with keys as x-axis labels and values as y-axis values.
        title: Optional plot title.
        xlabel: Optional x-axis label.
        ylabel: Optional y-axis label.

    Returns:
        Matplotlib Figure object.
    """
    fig, ax = plt.subplots()

    keys = []
    for k in data.keys():
        keys.append(k)

    values = []
    for v in data.values():
        values.append(v)

    ax.bar(keys, values)

    if title:
        ax.set_title(title)
    if xlabel:
        ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)

    ax.tick_params(axis="x", rotation=45)
    fig.tight_layout()

    return fig


@click.command()
@click.argument("input_path", type=str)
@click.option("--split", "-s", default="test", help="Data split to plot (train/test)")
@click.option("--title", "-t", default=None, help="Plot title")
@click.option("--xlabel", "-x", default=None, help="X-axis label")
@click.option("--ylabel", "-y", default=None, help="Y-axis label")
@click.option("--output", "-o", default="out/evaluation_plot.png", help="Output file path")
def plot(input_path, split, title, xlabel, ylabel, output):
    """Create a bar plot from metrics JSON and save to file.

    INPUT_PATH: Path to metrics JSON file from evaluate, or a JSON string.
    """
    # Check if input is a file path
    input_file = Path(input_path)

    if input_file.exists() and input_file.suffix == ".json":
        click.echo("Loading metrics from %s..." % input_path)
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Handle metrics format with train/test splits
        if split in data:
            data = data[split]
        else:
            # If no split found, use the data as-is (flat dict)
            pass
    else:
        # Try to parse as JSON string
        try:
            data = json.loads(input_path)
        except json.JSONDecodeError:
            raise click.UsageError("Invalid JSON input: %s" % input_path)

    # Ensure output directory exists
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig = plot_bar(data, title=title, xlabel=xlabel, ylabel=ylabel)
    fig.savefig(output_path)
    click.echo("Plot saved to %s" % output_path)


# CLI entry point: python -m hw1.utils --help
if __name__ == "__main__":
    plot()
