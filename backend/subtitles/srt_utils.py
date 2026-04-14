from dataclasses import dataclass


@dataclass
class SubtitleEntry:
    index: int
    timestamp: str
    text: str


def parse_srt(content: str) -> list[SubtitleEntry]:
    blocks = [block.strip() for block in content.strip().split('\n\n') if block.strip()]
    entries = []

    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            raise ValueError('Invalid SRT block')

        index = int(lines[0].strip())
        timestamp = lines[1].strip()
        text = '\n'.join(lines[2:]).strip()
        entries.append(SubtitleEntry(index=index, timestamp=timestamp, text=text))

    return entries


def serialize_srt(entries: list[SubtitleEntry]) -> str:
    serialized = []
    for entry in entries:
        serialized.append(f"{entry.index}\n{entry.timestamp}\n{entry.text}")
    return '\n\n'.join(serialized) + '\n'
