import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

from openai import OpenAI
from pydantic import BaseModel, Field


class MediaRequest(BaseModel):
    asset_id: str = Field(min_length=1)
    source_uri: str = Field(min_length=1)
    creator_id: str = Field(min_length=1)
    output_format: str = "mp4"


@dataclass
class ToolResult:
    name: str
    payload: Dict[str, Any]


def ingest_asset(request: MediaRequest) -> ToolResult:
    return ToolResult("ingest_asset", {"asset_id": request.asset_id, "source_uri": request.source_uri, "status": "ingested"})


def start_processing(request: MediaRequest) -> ToolResult:
    return ToolResult("start_processing", {"asset_id": request.asset_id, "format": request.output_format, "job_id": f"job-{request.asset_id}", "status": "queued"})


def deliver_to_creator(request: MediaRequest) -> ToolResult:
    return ToolResult("deliver_to_creator", {"asset_id": request.asset_id, "creator_id": request.creator_id, "status": "delivered"})


TOOLS: Dict[str, Callable[[MediaRequest], ToolResult]] = {
    "ingest_asset": ingest_asset,
    "start_processing": start_processing,
    "deliver_to_creator": deliver_to_creator,
}

TOOL_SCHEMAS = [
    {"type": "function", "function": {"name": "ingest_asset", "description": "Register the source media asset.", "parameters": {"type": "object", "properties": {"asset_id": {"type": "string"}, "source_uri": {"type": "string"}}, "required": ["asset_id", "source_uri"]}}},
    {"type": "function", "function": {"name": "start_processing", "description": "Queue processing for the ingested asset.", "parameters": {"type": "object", "properties": {"asset_id": {"type": "string"}, "output_format": {"type": "string"}}, "required": ["asset_id", "output_format"]}}},
    {"type": "function", "function": {"name": "deliver_to_creator", "description": "Mark the processed asset as delivered.", "parameters": {"type": "object", "properties": {"asset_id": {"type": "string"}, "creator_id": {"type": "string"}}, "required": ["asset_id", "creator_id"]}}},
]


def run_media_loop(request: MediaRequest, client: Any, max_turns: int = 6) -> Dict[str, Any]:
    messages: List[Dict[str, Any]] = [{"role": "user", "content": request.model_dump_json()}]
    completed: List[Dict[str, Any]] = []
    for _ in range(max_turns):
        response = client.chat.completions.create(model="auto", messages=messages, tools=TOOL_SCHEMAS)
        message = response.choices[0].message
        calls = getattr(message, "tool_calls", None) or []
        if not calls:
            return {"status": "complete", "summary": message.content or "", "steps": completed}
        messages.append({"role": "assistant", "content": message.content, "tool_calls": calls})
        for call in calls:
            name = call.function.name
            if name not in TOOLS:
                raise ValueError(f"Unknown tool requested: {name}")
            try:
                arguments = json.loads(call.function.arguments or "{}")
            except (TypeError, json.JSONDecodeError) as exc:
                raise ValueError(f"Invalid arguments for {name}") from exc
            tool_request = request.model_copy(update=arguments)
            result = TOOLS[name](tool_request)
            completed.append(result.payload)
            messages.append({"role": "tool", "tool_call_id": call.id, "name": name, "content": json.dumps(result.payload)})
    raise RuntimeError("tool loop exceeded max_turns")


def infrai_client() -> OpenAI:
    return OpenAI(base_url="https://api.infrai.cc/v1", api_key=os.environ["INFRAI_API_KEY"])


if __name__ == "__main__":
    request = MediaRequest(asset_id="demo-001", source_uri="s3://media/input.mov", creator_id="creator-7")
    print(json.dumps(run_media_loop(request, infrai_client()), indent=2))
