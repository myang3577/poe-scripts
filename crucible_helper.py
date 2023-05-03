class CrucibleHelper:
    @staticmethod
    def extract_from_items(items):
        return [
            {
                "name": item["item"]["name"],
                "baseType": item["item"]["baseType"],
                # "whisper_token": item["listing"].get("whisper_token"),
                # "whisper": item["listing"].get("whisper"),
                "price": item["listing"].get("price"),
                "crucible_nodes": item["item"]["crucible"]["nodes"],
            }
            for item in items
        ]

    @staticmethod
    def extract_node(extracted_items, search_text):
        extracted_items_with_nodes = []

        for extracted_item in extracted_items:
            node = CrucibleHelper.find_node(
                nodes=extracted_item["crucible_nodes"], search_text=search_text
            )
            if not node:
                continue

            new_item = extracted_item | {"node": node}

            extracted_items_with_nodes += [new_item]

        return extracted_items_with_nodes

    @staticmethod
    def find_node(nodes, search_text):
        if isinstance(nodes, dict):
            nodes = list(nodes.values())

        for node in nodes:
            for stat in node["stats"]:
                if search_text.lower() in stat.lower():
                    return node
