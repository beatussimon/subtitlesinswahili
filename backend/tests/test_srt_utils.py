from subtitles.srt_utils import parse_srt, serialize_srt


SRT_SAMPLE = """1
00:00:01,000 --> 00:00:02,500
Hello world

2
00:00:03,000 --> 00:00:04,500
How are you?
"""


def test_parse_srt_preserves_timestamps_and_text():
    entries = parse_srt(SRT_SAMPLE)

    assert len(entries) == 2
    assert entries[0].timestamp == '00:00:01,000 --> 00:00:02,500'
    assert entries[0].text == 'Hello world'
    assert entries[1].timestamp == '00:00:03,000 --> 00:00:04,500'


def test_serialize_round_trip():
    entries = parse_srt(SRT_SAMPLE)
    serialized = serialize_srt(entries)

    assert '00:00:01,000 --> 00:00:02,500' in serialized
    assert 'How are you?' in serialized
