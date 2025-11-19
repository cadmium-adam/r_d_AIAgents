import json
from typing import TypedDict, Literal, List, Optional
from pathlib import Path

# -------------------------------
# Data Models
# -------------------------------

class Entity(TypedDict):
    name: str
    entityType: str
    observations: List[str]


class Relation(TypedDict):
    from_: str  
    to: str
    relationType: str


class KnowledgeGraph(TypedDict):
    entities: List[Entity]
    relations: List[Relation]


# -------------------------------
# Graph Manager
# -------------------------------

class KnowledgeGraphManager:
    def __init__(self, path: Path):
        self.path = path

    def _read_lines(self) -> List[str]:
        if not self.path.exists():
            return []
        return self.path.read_text(encoding="utf-8").splitlines()

    def _load_graph(self) -> KnowledgeGraph:
        lines = self._read_lines()
        graph: KnowledgeGraph = {"entities": [], "relations": []}
        for line in lines:
            item = json.loads(line)
            if item.get("type") == "entity":
                graph["entities"].append(item)
            elif item.get("type") == "relation":
                graph["relations"].append(item)
        return graph

    def _save_graph(self, graph: KnowledgeGraph):
        lines = [
            json.dumps({"type": "entity", **e}) for e in graph["entities"]
        ] + [
            json.dumps({"type": "relation", **r}) for r in graph["relations"]
        ]
        self.path.write_text("\n".join(lines), encoding="utf-8")

    async def create_entities(self, entities: List[Entity]):
        graph = self._load_graph()
        new = [e for e in entities if not any(x["name"] == e["name"] for x in graph["entities"])]
        graph["entities"].extend(new)
        self._save_graph(graph)
        return new

    async def create_relations(self, relations: List[Relation]):
        graph = self._load_graph()
        new = [
            r for r in relations if not any(
                x["from_"] == r["from_"] and x["to"] == r["to"] and x["relationType"] == r["relationType"]
                for x in graph["relations"]
            )
        ]
        graph["relations"].extend(new)
        self._save_graph(graph)
        return new

    async def add_observations(self, observations):
        graph = self._load_graph()
        results = []
        for obs in observations:
            entity = next((e for e in graph["entities"] if e["name"] == obs["entityName"]), None)
            if not entity:
                raise ValueError(f"Entity {obs['entityName']} not found")
            new_obs = [c for c in obs["contents"] if c not in entity["observations"]]
            entity["observations"].extend(new_obs)
            results.append({"entityName": obs["entityName"], "addedObservations": new_obs})
        self._save_graph(graph)
        return results

    async def delete_entities(self, names: List[str]):
        graph = self._load_graph()
        graph["entities"] = [e for e in graph["entities"] if e["name"] not in names]
        graph["relations"] = [r for r in graph["relations"] if r["from_"] not in names and r["to"] not in names]
        self._save_graph(graph)

    async def delete_observations(self, deletions):
        graph = self._load_graph()
        for d in deletions:
            entity = next((e for e in graph["entities"] if e["name"] == d["entityName"]), None)
            if entity:
                entity["observations"] = [o for o in entity["observations"] if o not in d["observations"]]
        self._save_graph(graph)

    async def delete_relations(self, relations: List[Relation]):
        graph = self._load_graph()
        graph["relations"] = [
            r for r in graph["relations"]
            if not any(r["from_"] == d["from_"] and r["to"] == d["to"] and r["relationType"] == d["relationType"]
                       for d in relations)
        ]
        self._save_graph(graph)

    async def read_graph(self):
        return self._load_graph()

    async def search_nodes(self, query: str):
        graph = self._load_graph()
        query_l = query.lower()
        filtered_entities = [
            e for e in graph["entities"]
            if query_l in e["name"].lower() or query_l in e["entityType"].lower() or
               any(query_l in o.lower() for o in e["observations"])
        ]
        names = set(e["name"] for e in filtered_entities)
        filtered_relations = [r for r in graph["relations"] if r["from_"] in names and r["to"] in names]
        return {"entities": filtered_entities, "relations": filtered_relations}

    async def open_nodes(self, names: List[str]):
        graph = self._load_graph()
        filtered_entities = [e for e in graph["entities"] if e["name"] in names]
        name_set = set(e["name"] for e in filtered_entities)
        filtered_relations = [r for r in graph["relations"] if r["from_"] in name_set and r["to"] in name_set]
        return {"entities": filtered_entities, "relations": filtered_relations}
