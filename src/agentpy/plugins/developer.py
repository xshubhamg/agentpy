import uuid
import json
import requests
from typing import Annotated, Any

def register(agent: Any) -> None:
    @agent.tool
    def generate_uuid() -> dict[str, str]:
        """Generate a random UUID v4."""
        return {"uuid": str(uuid.uuid4())}

    @agent.tool
    def format_json(json_string: Annotated[str, "The JSON string to format"]) -> dict[str, Any]:
        """Pretty-print a JSON string."""
        try:
            data = json.loads(json_string)
            return {"formatted": json.dumps(data, indent=2)}
        except Exception as e:
            return {"error": str(e)}

    @agent.tool
    def get_ip() -> dict[str, str]:
        """Get the current public IP address."""
        try:
            resp = requests.get("https://api.ipify.org?format=json")
            return resp.json()
        except Exception as e:
            return {"error": str(e)}
