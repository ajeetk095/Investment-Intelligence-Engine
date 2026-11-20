"""Plotly chart builders (dark/light theme handled by Streamlit templates)."""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

TEMPLATE = "plotly_dark"


def price_chart(prices: pd.DataFrame, normalized: bool = False) -> go.Figure:
    df = prices.copy()
    if normalized:
        df = df / df.iloc[0] * 100
    fig = px.line(df, template=TEMPLATE)
    fig.update_layout(xaxis_title="Date", yaxis_title="Index (start = 100)" if normalized else "Price (USD)",
                      legend_title="Ticker", hovermode="x unified", height=460)
    return fig


def correlation_heatmap(corr: pd.DataFrame) -> go.Figure:
    fig = go.Figure(go.Heatmap(z=corr.values, x=corr.columns, y=corr.index,
                               zmin=-1, zmax=1, colorscale="RdBu", zmid=0,
                               text=corr.round(2).values, texttemplate="%{text}"))
    fig.update_layout(template=TEMPLATE, height=460, title="Correlation heatmap")
    return fig


def weights_bar(weights: dict[str, pd.Series], title: str) -> go.Figure:
    fig = go.Figure()
    for name, w in weights.items():
        fig.add_bar(name=name, x=w.index, y=w.values)
    fig.update_layout(barmode="group", template=TEMPLATE, title=title,
                      yaxis_title="Weight", xaxis_title="Asset", height=440)
    return fig


def frontier_chart(frontier: pd.DataFrame, asset_vols: dict[str, float],
                   asset_rets: dict[str, float], best: dict | None = None) -> go.Figure:
    fig = go.Figure()
    fig.add_scatter(x=frontier["volatility"], y=frontier["target_return"],
                    mode="lines", name="Efficient frontier")
    fig.add_scatter(x=list(asset_vols.values()), y=list(asset_rets.values()),
                    mode="markers+text", text=list(asset_vols.keys()),
                    textposition="top center", name="Assets")
    if best:
        fig.add_scatter(x=[best["volatility"]], y=[best["return"]], mode="markers+text",
                        text=["Max Sharpe"], textposition="bottom center",
                        marker=dict(size=14, symbol="star"), name="Optimal")
    fig.update_layout(template=TEMPLATE, xaxis_title="Annualized volatility",
                      yaxis_title="Annualized return", height=480)
    return fig


def histogram_compare(series_map: dict[str, pd.Series], title: str) -> go.Figure:
    fig = go.Figure()
    for name, s in series_map.items():
        fig.add_histogram(x=s, name=name, opacity=0.6, nbinsx=60, histnorm="probability density")
    fig.update_layout(barmode="overlay", template=TEMPLATE, title=title,
                      xaxis_title="Return", yaxis_title="Density", height=440)
    return fig


def monte_carlo_fan(terminal_pct: dict, horizon_label: str) -> go.Figure:
    fig = go.Figure()
    keys = [5, 25, 50, 75, 95]
    labels = ["p5", "p25", "p50", "p75", "p95"]
    vals = [terminal_pct[k] for k in keys]
    fig.add_bar(x=labels, y=vals, marker_color=["#e74c3c", "#e67e22", "#f1c40f", "#2ecc71", "#27ae60"])
    fig.update_layout(template=TEMPLATE, title=f"Bootstrap forecast - terminal return ({horizon_label})",
                      xaxis_title="Percentile", yaxis_title="Return", height=400)
    return fig
