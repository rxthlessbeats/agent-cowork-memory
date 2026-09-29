def native_id(obj, path):
    return path.parent.name or None


def visible(obj):
    if obj.get("type") == "turn_ended" or "role" not in obj:
        return "skip", []
    role = obj.get("role")
    if role not in ("user", "assistant"):
        return "skip", []
    content = (obj.get("message") or {}).get("content")
    if isinstance(content, str):
        return "message", [{"role": role, "text": content, "timestamp": None}]
    if not isinstance(content, list):
        return "unknown", []
    texts = []
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use":
            continue
        if block.get("type") == "text" and block.get("text"):
            texts.append(block["text"])
        elif block.get("type") not in ("text", "tool_use"):
            return "unknown", []
    if not texts:
        return "skip", []
    return "message", [{"role": role, "text": "\n".join(texts), "timestamp": None}]
