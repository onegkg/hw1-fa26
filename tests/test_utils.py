"""Tests for utils module."""

import pytest
from matplotlib.figure import Figure

from utils import plot_bar


class TestPlotBar:
    """Tests for plot_bar function."""

    def test_returns_figure(self) -> None:
        data = {"a": 1, "b": 2, "c": 3}
        fig = plot_bar(data)
        assert isinstance(fig, Figure)

    def test_with_title(self) -> None:
        data = {"x": 1, "y": 2}
        fig = plot_bar(data, title="Test Title")
        ax = fig.axes[0]
        assert ax.get_title() == "Test Title"

    def test_with_labels(self) -> None:
        data = {"x": 1, "y": 2}
        fig = plot_bar(data, xlabel="X Label", ylabel="Y Label")
        ax = fig.axes[0]
        assert ax.get_xlabel() == "X Label"
        assert ax.get_ylabel() == "Y Label"

    def test_with_float_values(self) -> None:
        data = {"accuracy": 0.85, "precision": 0.90, "recall": 0.80}
        fig = plot_bar(data)
        assert isinstance(fig, Figure)

    def test_empty_data(self) -> None:
        data = {}
        fig = plot_bar(data)
        assert isinstance(fig, Figure)
