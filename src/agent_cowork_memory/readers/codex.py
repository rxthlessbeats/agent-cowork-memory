_SKIP_TYPES = {"session_meta", "event_msg", "token_usage_record", "turn_context", "world_state"}
_SKIP_PAYLOAD = {"reasoning", "function_call", "function_call_output", "custom_tool_call", "custom_tool_call_output"}


def native_id(obj, path):
    payload = obj.get("payload") or {}
    if obj.get("type") == "session_meta" and payload.get("session_id"):
        return payload["session_id"]
    return None


def visible(obj):
    kind = obj.get("type")
    if kind in _SKIP_TYPES:
        return "skip", []
    if kind != "response_item":
        return "unknown", []
    payload = obj.get("payload") or {}
    ptype = payload.get("type")
    if ptype in _SKIP_PAYLOAD or payload.get("role") == "developer":
        return "skip", []
    if ptype != "message" or payload.get("role") not in ("user", "assistant"):
        return "unknown", []
    texts = []
    for block in payload.get("content") or []:
        if isinstance(block, dict) and block.get("type") in ("input_text", "output_text") and block.get("text"):
            if not block["text"].lstrip().startswith(("<environment_context>", "# AGENTS.md instructions")):
                texts.append(block["text"])
    if not texts:
        return "skip", []
    return "message", [{"role": payload["role"], "text": "\n".join(texts), "timestamp": obj.get("timestamp")}]
