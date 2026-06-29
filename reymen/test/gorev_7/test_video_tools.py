"""Video araçları birim testleri."""

from __future__ import annotations

import subprocess
import sys
from unittest.mock import patch, MagicMock

import pytest

from reymen import video_tools
from reymen.video_tools import (
    VideoToolError,
    VideoInfo,
    FFmpegResult,
    check_available,
    ensure_tool,
    download,
    convert,
    probe,
    cut,
    extract_audio,
)


class TestCheckAvailable:
    def test_returns_dict(self):
        result = check_available()
        assert isinstance(result, dict)
        assert "yt-dlp" in result
        assert "ffmpeg" in result
        assert "ffprobe" in result
        assert all(isinstance(v, bool) for v in result.values())


class TestEnsureTool:
    def test_ensure_existing_tool(self):
        # python her zaman var
        path = ensure_tool("python") if sys.platform == "win32" else ensure_tool("python3")
        assert path is not None

    def test_ensure_missing_tool(self):
        with pytest.raises(VideoToolError, match="bulunamadı"):
            ensure_tool("nonexistent_tool_xyz_123")


class TestDownload:
    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/yt-dlp")
    def test_download_success(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout='{"title": "Test Video", "duration": 120.5, "uploader": "tester"}',
            stderr="",
        )
        info = download("https://example.com/video")
        assert isinstance(info, VideoInfo)
        assert info.url == "https://example.com/video"
        assert info.title == "Test Video"
        assert info.duration == 120.5

    @patch("reymen.video_tools._find_tool", return_value=None)
    def test_download_no_ytdlp(self, mock_find):
        with pytest.raises(VideoToolError, match="yt-dlp"):
            download("https://example.com/video")

    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/yt-dlp")
    def test_download_failure(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        with pytest.raises(VideoToolError, match="başarısız"):
            download("https://example.com/video")

    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/yt-dlp")
    def test_download_audio_only(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout='{"title": "Audio"}', stderr=""
        )
        info = download("https://example.com/audio", audio_only=True)
        assert info.title == "Audio"
        # audio_only flag'ının komuta eklendiğini kontrol et
        cmd = mock_run.call_args[0][0]
        assert "-x" in cmd
        assert "--audio-format" in cmd

    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/yt-dlp")
    def test_download_timeout(self, mock_find, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="yt-dlp", timeout=5)
        with pytest.raises(VideoToolError, match="timeout"):
            download("https://example.com/video", timeout=5)


class TestProbe:
    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/ffprobe")
    def test_probe_success(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0, stdout='{"format": {"duration": "10.5"}}', stderr=""
        )
        result = probe("video.mp4")
        assert result["format"]["duration"] == "10.5"

    @patch("reymen.video_tools._find_tool", return_value=None)
    def test_probe_no_ffprobe(self, mock_find):
        with pytest.raises(VideoToolError):
            probe("video.mp4")


class TestConvert:
    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/ffmpeg")
    def test_convert_success(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = convert("in.mp4", "out.mp3", format="mp3")
        assert isinstance(result, FFmpegResult)
        assert result.success is True

    @patch("reymen.video_tools._find_tool", return_value=None)
    def test_convert_no_ffmpeg(self, mock_find):
        with pytest.raises(VideoToolError):
            convert("in.mp4", "out.mp3")

    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/ffmpeg")
    def test_convert_failure(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="error")
        with pytest.raises(VideoToolError, match="başarısız"):
            convert("in.mp4", "out.mp3")


class TestExtractAudio:
    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/ffmpeg")
    def test_extract_audio_mp3(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = extract_audio("video.mp4", "audio.mp3")
        assert result.success is True
        cmd = mock_run.call_args[0][0]
        assert "libmp3lame" in cmd


class TestCut:
    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/ffmpeg")
    def test_cut_with_duration(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = cut("in.mp4", "out.mp4", start="00:00:10", duration="00:00:30")
        assert result.success is True

    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/ffmpeg")
    def test_cut_with_end(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        result = cut("in.mp4", "out.mp4", start="10", end="40")
        assert result.success is True

    def test_cut_duration_and_end_conflict(self):
        with pytest.raises(ValueError, match="birlikte kullanılamaz"):
            cut("in.mp4", "out.mp4", start="0", duration="10", end="20")

    @patch("reymen.video_tools.subprocess.run")
    @patch("reymen.video_tools._find_tool", return_value="/usr/bin/ffmpeg")
    def test_cut_copy_codecs(self, mock_find, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        cut("in.mp4", "out.mp4", start="0", duration="10", copy_codecs=True)
        cmd = mock_run.call_args[0][0]
        assert "-c" in cmd
        assert "copy" in cmd


class TestDataclasses:
    def test_video_info_as_dict(self):
        info = VideoInfo(url="http://x", title="T")
        d = info.as_dict()
        assert d["url"] == "http://x"
        assert d["title"] == "T"

    def test_ffmpeg_result_as_dict(self):
        r = FFmpegResult(success=True, command=["ffmpeg"], returncode=0)
        d = r.as_dict()
        assert d["success"] is True
        assert d["returncode"] == 0