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


def get_query_url(query):
    query = json.dumps(query)
    query = urllib.parse.quote(query)
    return f"https://www.pathofexile.com/trade/search/Crucible?q={query}"


def add_name_to_query(query, name):
    query = copy.deepcopy(query)
    query["query"]["term"] = name
    return query


def valid_pos_conditions(item, pos_conditions):
    valid = valid_node_pos(item["node"], pos_conditions.get("valid_pos_list", []))
    valid = valid and valid_empty_pos(
        item["crucible_nodes"], pos_conditions.get("empty_pos_list", [])
    )

    return valid


def valid_node_pos(node, valid_pos_list):
    if not valid_pos_list:
        return True

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


def augment_filtered_items_with_named_url(filtered_items, query):
    return [
        {
            "named_url": get_query_url(query=add_name_to_query(query, item["name"]))
            if item["name"]
            else "empty name"
        }
        | item
        for item in filtered_items
    ]


def main():
    parser = argparse.ArgumentParser(description="Find crucible weapons to combine")
    parser.add_argument(
        "--input_file", type=str, required=False, default="crucible_node_to_find.json"
    )
    parser.add_argument("-c", type=int, required=False, default=100)

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
        search_texts=input["crucible_mod_search_text"],
    )

    LOG.info(f"Found [{len(items_with_node)}] items for query.")

    LOG.info(f"Filtering items with valid node position.")

    filtered_items = [
        item
        for item in items_with_node
        if valid_pos_conditions(item=item, pos_conditions=input["pos_conditions"])
    ]
    filtered_items = augment_filtered_items_with_named_url(
        filtered_items=filtered_items, query=input["query"]
    )

    LOG.info(f"Found [{len(filtered_items)}] items.")

    filtered_query = augment_query_with_filtered_items(filtered_items, input["query"])
    filtered_url = get_query_url(filtered_query)

    filtered_items = [{"filtered_url": filtered_url}] + filtered_items

    with open("items_with_node.json", "w") as f:
        json.dump(items_with_node, f, indent=4)
    with open("filtered_items.json", "w") as f:
        json.dump(filtered_items, f, indent=4)


if __name__ == "__main__":
    main()
