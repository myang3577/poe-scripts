class CrucibleHelper:
    @staticmethod
    def extract_from_items(items):
        return [
            {
                "name": item["item"]["name"],
                "baseType": item["item"]["baseType"],
                # "whisper_token": item["listing"].get("whisper_token"),
                "whisper": item["listing"].get("whisper"),
                "price": item["listing"].get("price"),
                "crucible_nodes": CrucibleHelper.__get_crucible_nodes(item),
            }
            for item in items
        ]

    @staticmethod
    def extract_node(extracted_items, search_texts):
        extracted_items_with_nodes = []

        for extracted_item in extracted_items:
            node = CrucibleHelper.find_node(
                nodes=extracted_item["crucible_nodes"], search_texts=search_texts
            )
            if not node:
                continue

            new_item = extracted_item | {"node": node}

            extracted_items_with_nodes += [new_item]

        return extracted_items_with_nodes

    @staticmethod
    def find_node(nodes, search_texts):
        if isinstance(nodes, dict):
            nodes = list(nodes.values())

        if not search_texts:
            return nodes

        for node in nodes:
            for stat in node["stats"]:
                if any(st.lower() in stat.lower() for st in search_texts):
                    return node

    @staticmethod
    def __get_crucible_nodes(item):
        crucible_nodes = item["item"]["crucible"]["nodes"]

        if isinstance(crucible_nodes, dict):
            return list(crucible_nodes.values())

        return crucible_nodes


a = {
    "query": {
        "status": {"option": "onlineleague"},
        # "term": "Name here",
        "stats": [
            {"type": "and", "filters": []},
            {"filters": [], "type": "crucible"},
            {
                "filters": [{"id": "crucible.mod_51047"}, {"id": "crucible.mod_2397"}],
                "type": "crucible",
                "value": {"min": 1},
            },
            {
                "filters": [{"id": "crucible.mod_58320"}],
                "type": "crucible",
                "value": {"min": 1},
            },
        ],
        "filters": {
            "type_filters": {"filters": {"category": {"option": "weapon.wand"}}}
        },
    },
    "sort": {"price": "asc"},
}
