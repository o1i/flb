def delete_verification(d: dict) -> bool:
    assert not set(d.keys()) - set(["id"])  # Presence of all required keys
    assert isinstance(d["id"], int)  # Name Format
    return True
