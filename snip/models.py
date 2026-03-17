from dataclasses import dataclass, field
from typing import List


@dataclass
class Snippet:
    key: str
    content: str
    tags: List[str] = field(default_factory=list)

