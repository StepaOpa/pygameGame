from dataclasses import dataclass
from typing import Any, Type

EntityId = str
Component = object


@dataclass
class StoredSystem:
    variables: dict[str, Any]
    components: dict[str, Type[Component]]  # key is argument name
    has_entity_id_argument: bool
    has_ecs_argument: bool
