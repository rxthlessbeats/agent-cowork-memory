_SKIP = {"queue-operation", "attachment", "atis-latch", "last-prompt", "cost-state", "system", "summary"}


def native_id(obj, path):
    return obj.get("sessionId") or path.stem


def visible(obj):
    kind = obj.get("type")
    if kind in _SKIP:
        return "skip", []
    if kind not in ("user", "assistant"):
        return "unknown", []
    content = (obj.get("message") or {}).get("content")
    role = kind
    if isinstance(content, str):
        return "message", [{"role": role, "text": content, "timestamp": obj.get("timestamp")}]
    if not isinstance(content, list):
        return "unknown", []
    texts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        btype = block.get("type")
        if btype in ("tool_use", "thinking", "tool_result"):
            continue
        if btype == "text" and block.get("text"):
            texts.append(block["text"])
        elif btype not in ("text",):
            return "unknown", []
    if not texts:
        return "skip", []
    return "message", [{"role": role, "text": "\n".join(texts), "timestamp": obj.get("timestamp")}]
