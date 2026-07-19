from pathlib import Path

from autoguard_edge.demo import run

if __name__ == "__main__":
    result = run(Path("outputs/edge_event.json"))
    print(result["event_id"], result["decision"])
