from datetime import datetime
import re


def post_verification(d: dict) -> bool:
    assert not set(d.keys()) - set(["name", "date", "start", "end"])  # Presence of all required keys
    assert re.match("^[a-zA-Z ]+$", d["name"])  # Name Format
    assert re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", d["date"])  # Date Format
    assert re.match("^[0-9]{2}:[0-9]{2}$", d["start"])  # Start Format
    assert re.match("^[0-9]{2}:[0-9]{2}$", d["end"])  # End Format
    return True


def extract_info(d: dict) -> dict:
    """Assumes a verified dict containing all necessary entries in the correct format"""
    name = d["name"]
    start = datetime.strptime(d["date"] + d["start"], "%Y-%m-%d%H:%M").timestamp()
    end = datetime.strptime(d["date"] + d["end"], "%Y-%m-%d%H:%M").timestamp()
    kw = datetime.strptime(d["date"], "%Y-%m-%d").isocalendar()[1]
    return {"name": name, "start": start, "end": end, "kw": kw}
