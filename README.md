# Python iterators as a tool for analysing a social network
A simple iterator-based approach for visualising a Slack social network presented in PyCon Ireland 2019.

The tool generates a [directed graph](https://en.wikipedia.org/wiki/Directed_graph) of all mentions on a Slack community, with users as nodes and edges for users mentioning one another.
The edge widths are weighted by the number of mentions between the two users and the node areas are proportional to the total mentions of that user. In addition nodes are colored with a shade of red corresponding to their [pagerank](https://en.wikipedia.org/wiki/PageRank), which provides a more global measure of a user's influence.

## Dependencies
- An admin Slack API key, to be provided via the `SLACK_ADMIN_TOKEN` env variable
- The [graphviz](https://graphviz.org/) system package (e.g. `sudo apt install graphviz`)
- Some Python requirements - `pip install -r requirements.txt`

## Usage
1. Run `./slack_mentions.py` to render your last week's Slack mentions into `output.svg` in the current directory
1. View `output.svg` in your browser or favorite image viewer
1. Gain valuable insights about your community dynamics

## Example (anonymous) social graph (generated on 2019-10-12)
![2019-10-12 Slack graph](/output.svg "2019-10-12 Slack graph")
