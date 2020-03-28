from datetime import datetime
import re


def post_verification_lb(d: dict) -> bool:
    assert not set(d.keys()) - set(["name", "date", "start", "end", "capacity", "participant_count"])  # Presence of all required keys
    assert re.match("^[a-zA-Z ]+$", d["name"])  # Name Format
    assert re.match("^[0-9]{4}-[0-9]{2}-[0-9]{2}$", d["date"])  # Date Format
    assert re.match("^[0-9]{2}:[0-9]{2}$", d["start"])  # Start Format
    assert re.match("^[0-9]{2}:[0-9]{2}$", d["end"])  # End Format
    assert re.match("^[0-9]+$", d["capacity"]) # capacity format
    assert re.match("^[0-9]+$", d["participant_count"]) # participant_count format
    return True


def extract_info_lb(d: dict) -> dict:
    """Assumes a verified dict containing all necessary entries in the correct format"""
    name = d["name"]
    start = datetime.strptime(d["date"] + d["start"], "%Y-%m-%d%H:%M").timestamp()
    end = datetime.strptime(d["date"] + d["end"], "%Y-%m-%d%H:%M").timestamp()
    kw = datetime.strptime(d["date"], "%Y-%m-%d").isocalendar()[1]
    capacity = int(d["capacity"])
    participant_count = int(d["participant_count"])
    return {"name": name, "start": start, "end": end, "kw": kw, "capacity": capacity,
            "participant_count": participant_count}


def post_verification_user(d: dict) -> bool:
    assert not set(d.keys()) - set(["email"])
    assert is_email(d["email"])
    return True


def is_email(email: str) -> bool:
    """Returns whether the string is a valid email address"""
    email_regex = "(?:[a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*|\"(?:[\x01-\x08\x0b\x0c\x0e-" \
                  "\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*\")@(?:(?:[a-z0-9]" \
                  "(?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9]" \
                  "[0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-" \
                  "\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"
    return bool(re.match(email_regex, email))
