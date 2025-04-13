from datetime import datetime


def get_frame_seconds(frame: str) -> int | None:
    frames = {
        "1m": 1 * 60,
        "5m": 5 * 60,
        "15m": 15 * 60,
        "30m": 30 * 60,
        "60m": 60 * 60,
        "1h": 60 * 60,
        "4h": 4 * 60 * 60,
        "12h": 12 * 60 * 60,
        "1d": 1 * 24 * 60 * 60,
        "1w": 1 * 7 * 24 * 60 * 60,
        "1M": 1 * 30 * 24 * 60 * 60,
        # Bitunix specific.
        "1": 1 * 60,
        "60": 60 * 60,
        "240": 4 * 60 * 60,
        "D": 1 * 24 * 60 * 60,
        "W": 1 * 7 * 24 * 60 * 60
    }
    try:
        return frames[frame]
    except KeyError:
        return None


def convert_iso_to_unix(time: str) -> int | float:
    dt = datetime.fromisoformat(time.replace("Z", "+00:00"))
    unix_milliseconds = int(dt.timestamp() * 1000)
    return unix_milliseconds
