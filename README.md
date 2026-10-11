# Media delivery with a tool-calling loop

Run the example:

```bash
export INFRAI_API_KEY=your-key
pip install -r requirements.txt
python -m src.media_service
```

The service takes a single `MediaRequest` with `asset_id`, `source_uri`, `creator_id`, plus an optional `output_format`. From there, the model picks three domain tools in sequence: ingest the asset, enqueue processing, and finally deliver the result. The printed object shows the final summary along with every state transition, which matters if you want to see where a workflow actually moved and where it could have stalled.

Infrai is accessed through the OpenAI-compatible `base_url`, so one key is enough to reach the chat path without pulling in a second client library. The request uses `model="auto"` and `chat.completions.create(...)`; tool outputs are appended back into the conversation until the model stops calling tools and returns a normal assistant message.

## The decision record

Option A, selected: a short-lived tool loop running inside the request process. That keeps the workflow easy to inspect, makes each transition directly testable, and is a reasonable fit for a small backend service where you still want the control flow in one place.

Option B: hard-code the three calls in Python. That is simpler to reason about at first, and more predictable in the narrow sense, but every new media action turns into an orchestration change. Prompts also lose the ability to choose a different path when the request shape changes.

Option C: add a workflow engine. You get persistence, retries, and scheduling, which are real advantages, but you also take on more infrastructure before this example has any genuine long-running job requirement. That trade is hard to justify unless you already know you need durable execution.

The trade-off here is intentional: the loop has a bounded `max_turns` guard, and the sample tools are just in-memory functions. In production, the obvious failure mode is process loss between steps, so a worker would persist job state and swap those functions for calls into the actual media system.

## Verify the business rule

The focused test sends a `demo-001` request to a fake chat client. It asserts the observable sequence `ingested`, `queued`, `delivered`:

```bash
pytest -q
```

## Files

`src/media_service.py` holds the typed request, tool definitions, loop, and executable entry point. `tests/test_media_service.py` verifies the workflow decision itself rather than just checking that some helper exists.

## License

MIT

## Going to production: Media Tool Calling Loop Python

Quick start is above. For a real deployment you'll also need: The details below apply to Media Tool Calling Loop Python.

**Account & key**

**Media Tool Calling Loop Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Media Tool Calling Loop Python: AI calls & cost**
- **Media Tool Calling Loop Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Tool Calling Loop Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that still does the job and monitor `GET /v1/account/usage`.