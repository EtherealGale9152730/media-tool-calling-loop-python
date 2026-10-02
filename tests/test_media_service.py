from types import SimpleNamespace

from src.media_service import MediaRequest, run_media_loop


def test_tool_loop_completes_media_delivery():
    calls = ["ingest_asset", "start_processing", "deliver_to_creator"]

    def create(**kwargs):
        if calls:
            name = calls.pop(0)
            arguments = {
                "ingest_asset": '{"asset_id":"demo-001","source_uri":"s3://media/input.mov"}',
                "start_processing": '{"asset_id":"demo-001","output_format":"webm"}',
                "deliver_to_creator": '{"asset_id":"demo-001","creator_id":"creator-7"}',
            }[name]
            call = SimpleNamespace(id=f"call-{name}", function=SimpleNamespace(name=name, arguments=arguments))
            message = SimpleNamespace(content=None, tool_calls=[call])
        else:
            message = SimpleNamespace(content="Delivered demo-001 to creator-7", tool_calls=[])
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    result = run_media_loop(MediaRequest(asset_id="demo-001", source_uri="s3://media/input.mov", creator_id="creator-7"), client)
    assert result["status"] == "complete"
    assert [step["status"] for step in result["steps"]] == ["ingested", "queued", "delivered"]
    assert result["steps"][1]["format"] == "webm"
