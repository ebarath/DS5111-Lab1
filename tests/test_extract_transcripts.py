import io
import sys
import json

from youtube_transcript_api import YouTubeTranscriptApi
from bin.extract_transcripts import main


class MockTranscriptContainer:
    def to_raw_data(self):
        return [
            {
                "start": 10.5,
                "text": "Automated container tracking loop text entry."
            }
        ]


def test_extract_transcripts_main_pipeline_stream(monkeypatch, capsys):

    def stubbed_fetch_route(self, video_id):
        return MockTranscriptContainer()

    monkeypatch.setattr(
        YouTubeTranscriptApi,
        "fetch",
        stubbed_fetch_route
    )

    mock_input_stream = io.StringIO("fake_video_999\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    main()

    captured_output = capsys.readouterr()

    stdout_lines = captured_output.out.strip().split("\n")

    assert len(stdout_lines) == 1

    parsed_json_line = json.loads(stdout_lines[0])

    assert parsed_json_line["video_id"] == "fake_video_999"
    assert "Automated container tracking" in parsed_json_line["raw_text"]


def test_extract_transcripts_handles_fetch_failure(
    monkeypatch,
    capsys
):

    def failing_fetch(self, video_id):
        raise Exception("Fetch failed")

    monkeypatch.setattr(
        YouTubeTranscriptApi,
        "fetch",
        failing_fetch
    )

    mock_input_stream = io.StringIO("bad_video\n")
    monkeypatch.setattr(sys, "stdin", mock_input_stream)

    main()

    captured_output = capsys.readouterr()

    assert captured_output.out.strip() == ""
