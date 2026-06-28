# -*- coding: utf-8 -*-
"""Test: neutts_synth.py — NeuTTS synthesis helper."""

from unittest.mock import patch, MagicMock
from tools import neutts_synth
import sys


def test_write_wav(tmp_path):
    """_write_wav should create a valid WAV file."""
    import numpy as np
    samples = np.array([0.0, 0.5, -0.5, 1.0, -1.0], dtype=np.float32)
    out_path = str(tmp_path / "test.wav")
    neutts_synth._write_wav(out_path, samples, sample_rate=24000)
    import struct
    with open(out_path, "rb") as f:
        header = f.read(4)
        assert header == b"RIFF"


def test_main_ref_audio_not_found():
    """Var olmayan dosya yolu ile sys.exit(1) çağrılır."""
    test_args = ["prog", "--text", "hello", "--out", "/tmp/out.wav",
                 "--ref-audio", "/nonexistent_NOSUCH/ref.wav",
                 "--ref-text", "/nonexistent_NOSUCH/ref.txt"]
    with patch.object(sys, "argv", test_args):
        with patch("sys.exit", side_effect=SystemExit(1)) as mock_exit:
            with patch("builtins.print"):
                try:
                    neutts_synth.main()
                except SystemExit:
                    pass
                mock_exit.assert_called_once_with(1)


def test_main_import_error(tmp_path):
    """neutts import edilemezse sys.exit(1)."""
    ref_audio = tmp_path / "ref.wav"
    ref_text = tmp_path / "ref.txt"
    ref_audio.write_text("dummy")
    ref_text.write_text("dummy text")

    test_args = ["prog", "--text", "hello", "--out", str(tmp_path / "out.wav"),
                 "--ref-audio", str(ref_audio),
                 "--ref-text", str(ref_text)]
    with patch.object(sys, "argv", test_args):
        with patch("sys.exit", side_effect=SystemExit(1)) as mock_exit:
            with patch("builtins.print"):
                try:
                    neutts_synth.main()
                except SystemExit:
                    pass
                mock_exit.assert_called_once_with(1)
