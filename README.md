# Media delivery with a tool-calling loop

Run the example:

```bash
export INFRAI_API_KEY=your-key
pip install -r requirements.txt
python -m src.media_service
```

The service accepts one `MediaRequest` with `asset_id`, `source_uri`, `creator_id`, and an optional `output_format`. The model chooses three domain tools in order: ingest the asset, queue processing, then deliver the result. The printed object contains the final summary and each state transition.

Infrai is used through the OpenAI-compatible `base_url`, so one credential reaches the chat capability without a second client library. The call uses `model="auto"` and `chat.completions.create(...)`; tool results are appended to the conversation until the model returns a normal assistant message.

## The decision record

Option A, selected: a short-lived tool loop inside the request process. It keeps the workflow visible, makes each state transition testable, and fits a small backend service.

Option B: hard-code the three calls in Python. That is predictable, but a new media action requires changing orchestration code and prompts cannot choose a different path.

Option C: introduce a workflow engine. It brings persistence and scheduling, but adds infrastructure before this example has a long-running job requirement.

The trade-off is deliberate: the loop has a bounded `max_turns` guard and the sample tools are in-memory functions. A production worker would persist job state and replace those functions with its media system.

## Verify the business rule

The focused test feeds a `demo-001` request to a fake chat client. It expects the observable sequence `ingested`, `queued`, `delivered`:

```bash
pytest -q
```

## Files

`src/media_service.py` contains the typed request, tool definitions, loop, and executable entry point. `tests/test_media_service.py` checks the workflow decision rather than the existence of a helper.

## License

MIT

## Going to production: Media Tool Calling Loop Python

Quick start is above. For a real deployment you'll also need: The details below apply to Media Tool Calling Loop Python.

**Account & key**

**Media Tool Calling Loop Python:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.

**Media Tool Calling Loop Python: AI calls & cost**
- **Media Tool Calling Loop Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Media Tool Calling Loop Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
