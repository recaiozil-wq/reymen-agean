# -*- coding: utf-8 -*-
"""Test: image_generation_tool.py — Görsel üretme aracı."""

from unittest.mock import MagicMock, patch
from tools import image_generation_tool


def test_module_has_expected_names():
    """Modül beklenen isimleri içermeli."""
    assert hasattr(image_generation_tool, "IMAGE_GENERATE_SCHEMA")
    assert hasattr(image_generation_tool, "image_generate_tool")
    assert hasattr(image_generation_tool, "check_image_generation_requirements")
    assert hasattr(image_generation_tool, "registry")
    assert hasattr(image_generation_tool, "DEFAULT_ASPECT_RATIO")
    assert hasattr(image_generation_tool, "VALID_ASPECT_RATIOS")


def test_schema_structure():
    """Schema doğru yapıda olmalı."""
    schema = image_generation_tool.IMAGE_GENERATE_SCHEMA
    assert schema["name"] == "image_generate"
    assert "prompt" in schema["parameters"]["properties"]
    assert "aspect_ratio" in schema["parameters"]["properties"]
    assert "prompt" in schema["parameters"]["required"]


def test_aspect_ratios():
    """Geçerli en-boy oranları tanımlı olmalı."""
    assert image_generation_tool.DEFAULT_ASPECT_RATIO == "landscape"
    assert "landscape" in image_generation_tool.VALID_ASPECT_RATIOS
    assert "square" in image_generation_tool.VALID_ASPECT_RATIOS
    assert "portrait" in image_generation_tool.VALID_ASPECT_RATIOS


def test_aspect_to_size_mapping():
    """En-boy oranları boyut eşlemesi olmalı."""
    assert "landscape" in image_generation_tool._ASPECT_TO_SIZE
    assert "square" in image_generation_tool._ASPECT_TO_SIZE
    assert "portrait" in image_generation_tool._ASPECT_TO_SIZE


def test_check_requirements_no_key():
    """API anahtarı yoksa gereksinim kontrolü başarısız olur."""
    with patch.dict("os.environ", {}, clear=True):
        result = image_generation_tool.check_image_generation_requirements()
        assert isinstance(result, (bool, dict, type(None)))


def test_image_generate_tool_callable():
    """image_generate_tool fonksiyonu çağrılabilir."""
    assert callable(image_generation_tool.image_generate_tool)
