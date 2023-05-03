import argparse
import itertools
import json
import logging

from crucible_helper import CrucibleHelper
from path_of_exile_client import PathOfExileClient
from utils import Utils

Utils.setup_logging()

LOG = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Find crucible weapons to combine")
    parser.add_argument("-o", type=int, required=True, default=None)
    parser.add_argument("-oi", type=int, required=True, default=None)
    parser.add_argument(
        "--input_file", type=str, required=False, default="crucible_node_to_find.json"
    )

    args = parser.parse_args()

    poe_client = PathOfExileClient(
        posessid="UPDATE_ME",
        username="UPDATE_ME",
    )

    with open(args.input_file) as f:
        input = json.load(f)

    items = poe_client.query_trade(payload=input["query"], result_count=30)
    extracted_items = CrucibleHelper.extract_from_items(items)
    items_with_node = CrucibleHelper.extract_node(
        extracted_items=extracted_items,
        search_text=input["crucible_mod_search_text"],
    )

    LOG.info(f"Found [{len(items_with_node)}] items for query.")

    orbit = args.o
    orbit_index = args.oi

    LOG.info(f"Filtering for orbit [{orbit}] and orbit index [{orbit_index}].")

    filtered_items = [
        item
        for item in items_with_node
        if item["node"]["orbit"] == orbit and item["node"]["orbitIndex"] == orbit_index
    ]

    LOG.info(f"Found [{len(filtered_items)}] items.")

    with open("items_with_node.json", "w") as f:
        json.dump(items_with_node, f, indent=4)
    with open("filtered_items.json", "w") as f:
        json.dump(filtered_items, f, indent=4)


if __name__ == "__main__":
    main()
