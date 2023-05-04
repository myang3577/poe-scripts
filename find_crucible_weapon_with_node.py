import argparse
import configparser
import copy
import json
import logging
import urllib.parse

from crucible_helper import CrucibleHelper
from path_of_exile_client import PathOfExileClient
from utils import Utils

Utils.setup_logging()

LOG = logging.getLogger(__name__)


def valid_pos_conditions(item, pos_conditions):
    valid = valid_node_pos(item["node"], pos_conditions.get("valid_pos_list", []))
    valid = valid and valid_empty_pos(
        item["crucible_nodes"], pos_conditions.get("empty_pos_list", [])
    )

    return valid


def valid_node_pos(node, valid_pos_list):
    return any(
        node["orbit"] == pos["o"] and node["orbitIndex"] == pos["oi"]
        for pos in valid_pos_list
    )


def valid_empty_pos(crucible_nodes, empty_pos_list):
    return not any(
        node["orbit"] == empty_pos["o"] and node["orbitIndex"] == empty_pos["oi"]
        for node in crucible_nodes
        for empty_pos in empty_pos_list
    )


def augment_query_with_filtered_items(filtered_items, query):
    new_query = copy.deepcopy(query)

    for i in range(2):
        skill_nums = [
            item["crucible_nodes"][min(i, len(item["crucible_nodes"]) - 1)]["skill"]
            for item in filtered_items
        ]
        filters = [{"id": f"crucible.mod_{n}"} for n in skill_nums]

        if not filters:
            continue

        stat_group = {
            "filters": filters,
            "type": "crucible",
            "value": {"min": 1},
        }

        new_query["query"]["stats"] += [stat_group]

    return new_query


def main():
    parser = argparse.ArgumentParser(description="Find crucible weapons to combine")
    parser.add_argument(
        "--input_file", type=str, required=False, default="crucible_node_to_find.json"
    )
    parser.add_argument("-c", type=int, required=False, default=30)

    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read("config.ini")
    posessid = config["POE"]["POESESSID"]
    username = config["POE"]["USERNAME"]

    poe_client = PathOfExileClient(posessid=posessid, username=username)

    with open(args.input_file) as f:
        input = json.load(f)

    items = poe_client.query_trade(payload=input["query"], result_count=args.c)
    extracted_items = CrucibleHelper.extract_from_items(items)
    items_with_node = CrucibleHelper.extract_node(
        extracted_items=extracted_items,
        search_text=input["crucible_mod_search_text"],
    )

    LOG.info(f"Found [{len(items_with_node)}] items for query.")

    LOG.info(f"Filtering items with valid node position.")

    filtered_items = [
        item
        for item in items_with_node
        if valid_pos_conditions(item=item, pos_conditions=input["pos_conditions"])
    ]

    LOG.info(f"Found [{len(filtered_items)}] items.")

    new_query = augment_query_with_filtered_items(filtered_items, input["query"])
    new_query = json.dumps(new_query)
    new_query = urllib.parse.quote(new_query)
    filtered_url = f"https://www.pathofexile.com/trade/search/Crucible?q={new_query}"

    filtered_items = [{"filtered_url": filtered_url}] + filtered_items

    with open("items_with_node.json", "w") as f:
        json.dump(items_with_node, f, indent=4)
    with open("filtered_items.json", "w") as f:
        json.dump(filtered_items, f, indent=4)


if __name__ == "__main__":
    main()
