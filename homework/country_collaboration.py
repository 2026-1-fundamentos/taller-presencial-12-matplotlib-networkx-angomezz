"""Country collaboration network visualization."""

import os
from collections import Counter
from itertools import combinations

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

DATA_URL = (
    "https://raw.githubusercontent.com/jdvelasq/datalabs/master/"
    "datasets/scopus-papers.csv"
)


def _extract_countries(affiliations: str) -> list[str]:
    """Extract unique countries from a semicolon-separated affiliations string."""
    if pd.isna(affiliations):
        return []

    countries = []
    for affiliation in affiliations.split(";"):
        affiliation = affiliation.strip()
        if affiliation:
            countries.append(affiliation.split(",")[-1].strip())
    return list(set(countries))


def make_plot(n_countries: int) -> None:
    """Build and save country collaboration outputs for the top countries."""
    os.makedirs("files", exist_ok=True)

    dataframe = pd.read_csv(DATA_URL)

    country_counts: Counter[str] = Counter()
    paper_countries: list[list[str]] = []

    for affiliations in dataframe["Affiliations"]:
        countries = _extract_countries(affiliations)
        paper_countries.append(countries)
        country_counts.update(countries)

    top_countries = [country for country, _ in country_counts.most_common(n_countries)]
    top_country_set = set(top_countries)

    countries_dataframe = pd.DataFrame(
        {
            "countries": top_countries,
            "count": [country_counts[country] for country in top_countries],
        }
    )
    countries_dataframe.to_csv("files/countries.csv", index=False)

    co_occurrences: Counter[tuple[str, str]] = Counter()
    for countries in paper_countries:
        filtered_countries = sorted(
            country for country in countries if country in top_country_set
        )
        for country_a, country_b in combinations(filtered_countries, 2):
            co_occurrences[(country_a, country_b)] += 1

    co_occurrences_dataframe = pd.DataFrame(
        [
            {"country_a": country_a, "country_b": country_b, "count": count}
            for (country_a, country_b), count in co_occurrences.items()
        ]
    )
    co_occurrences_dataframe.to_csv("files/co_occurrences.csv", index=False)

    graph = nx.Graph()
    for country in top_countries:
        graph.add_node(country, count=country_counts[country])

    for (country_a, country_b), count in co_occurrences.items():
        graph.add_edge(country_a, country_b, weight=count)

    node_sizes = [country_counts[country] * 5 for country in graph.nodes()]
    edge_widths = [graph[u][v]["weight"] for u, v in graph.edges()]
    positions = nx.spring_layout(graph, seed=42)

    plt.figure(figsize=(12, 10))
    nx.draw_networkx_nodes(
        graph,
        positions,
        node_size=node_sizes,
        node_color="lightblue",
        alpha=0.9,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        width=edge_widths,
        alpha=0.5,
        edge_color="gray",
    )
    nx.draw_networkx_labels(graph, positions, font_size=8)
    plt.title("Country Collaboration Network")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("files/network.png", dpi=150)
    plt.close()
