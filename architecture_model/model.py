from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Dict, Any
import json


@dataclass
class Component:
    id: str
    name: str
    responsibility: str = ""
    layer: str = ""
    files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class Relationship:
    source: str
    target: str
    type: str


@dataclass
class ArchitectureSnapshot:
    version: str
    commit_hash: str
    components: List[Component] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    violations: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )

    def to_dict(self):
        return asdict(self)

    def save_json(self, output_path: str):
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                self.to_dict(),
                f,
                indent=4,
                ensure_ascii=False
            )