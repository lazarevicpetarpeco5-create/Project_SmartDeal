from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class AnalysisResult:
    summary: str
    client_requirements: str
    action_items: str
    follow_up_email: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AnalysisResult":
        return cls(
            summary=data.get("summary", ""),
            client_requirements=data.get("client_requirements", ""),
            action_items=data.get("action_items", ""),
            follow_up_email=data.get("follow_up_email", "")
        )