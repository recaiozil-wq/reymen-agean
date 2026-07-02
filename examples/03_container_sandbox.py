#!/usr/bin/env python3
"""Ornek 3: Container Sandbox ile guvenli kod calistirma."""
from src.reymen.guvenlik.container_sandbox import sandbox_al, ContainerConfig

cfg = ContainerConfig(sandbox_mode="kismi")
sb = sandbox_al(cfg)
print(f"Sandbox: {sb.aktif}")
print(sb.calistir("echo 'Container'da calisiyorum'"))
