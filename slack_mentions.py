#!/usr/bin/env python3
import re
from itertools import count
from collections import defaultdict, Counter
import os

import graphviz
import networkx
import slack

MESSAGES_PER_PAGE = 100  # This is the current API max
SLACK_CLIENT = slack.WebClient(os.environ['SLACK_ADMIN_TOKEN'])

# Tagged users appear as `<@UF123D5G7>`, so we use a capturing group on these
USER_ID_RE = re.compile("<@([A-Z0-9]{9})>")


def fetch_user_mentions():
    """Fetch all Slack messages of past week which contain @ mentions"""
    query = f"@* during:week"
    for page in count(1):
        data = SLACK_CLIENT.search_messages(query=query, page=page,
                                            count=MESSAGES_PER_PAGE).data
        yield from data['messages']['matches']
        if page >= data['messages']['pagination']['page_count']:
            break


def extract_mentions(messages):
    """Transform a sequence of messages into a sequence of mentions tuples"""
    # An autoincrementing integer anonymiser
    anonymiser = defaultdict(count().__next__)

    for message in messages:
        author = message['user']
        users_mentioned = USER_ID_RE.findall(message['text'])
        # Yield author,mentioned pairs of anonymous id's
        yield from ((anonymiser[author], anonymiser[mentioned])
                    for mentioned in users_mentioned)


def calculate_normalized_pagerank(mentions):
    """Calculate Pagerank values for mentions, in the range [0,1]"""
    nx_digraph = networkx.DiGraph()

    for (author, mentioned), mention_count in mentions.items():
        nx_digraph.add_edge(author, mentioned, weight=mention_count)

    pr = networkx.pagerank(nx_digraph)
    largest = max(pr.values())
    return {k: v/largest for k, v in pr.items()}


def render_graph(mentions, filename="output"):
    """Render a mentions counter to a graphviz digraph

    Note: we could have also rendered the graph with networkx, but it doesn't
    have graphviz's amazing no overlap functionality.
    """
    dot = graphviz.Digraph(format="svg", graph_attr={
                           "tooltip": " ", "overlap": "false"})

    normalized_pr = calculate_normalized_pagerank(mentions)

    # Calculate node weights
    node_weights = defaultdict(int)
    for (_, mentioned), mention_count in mentions.items():
        node_weights[mentioned] += mention_count

    # Add nodes
    for author, weight in node_weights.items():
        # Make area proportional to mention count
        size = int(0.5 * weight**0.5)
        fontsize = max(25*size, 10)
        pagerank = f"{normalized_pr[author]:.3f}"
        # Color using the HSV space, with pagerank as saturation of red
        fillcolor = f"0.000 {pagerank} 1.000"
        dot.node(f"S{author}", width=str(size), height=str(size),
                 fontsize=str(fontsize), style="filled", fillcolor=fillcolor,
                 tooltip=(f"S{author} was mentioned a total of {weight} "
                          f"time(s), with normalized pagerank of {pagerank}"))

    # Add edges
    for (author, mentioned), mention_count in mentions.items():
        dot.edge(f"S{author}", f"S{mentioned}", penwidth=str(mention_count),
                 tooltip=(f"S{author} mentioned S{mentioned} "
                          f"{mention_count} time(s)"))

    dot.render(filename)


if __name__ == "__main__":
    mention_iterator = extract_mentions(fetch_user_mentions())
    mentions = Counter(mention_iterator)
    render_graph(mentions)
