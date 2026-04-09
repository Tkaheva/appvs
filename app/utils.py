def format_duration(seconds):
    minutes = int(seconds // 60)
    seconds_remainder = int(seconds % 60)
    return f"{minutes}:{seconds_remainder:02d}"

def format_timestamp(seconds):
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes:02d}:{secs:02d}"
