from pathlib import Path

def load_queries(base_path="queries"):
    print("loading queries")
    """Auto-discover SQL files in queries/ and return dict {name: path}."""
    queries = {}
    print("looking in",base_path )
    for file in Path(base_path).rglob("*"):
        # name will be folder_file, e.g. revenue_total_revenue
        if file.suffix.lower() in [".sql", ".py"]:
            print("loading: ", file)
            name = f"{file.parent.name}_{file.stem}"
            queries[name] = str(file)
    return queries
