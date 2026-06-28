---
skill_id: e94e1ece60d7
usage_count: 1
last_used: 2026-06-16
---
# Minimal rights: SET_QUOTA (0x0100) | TERMINATE (0x0001)
    PROCESS_SET_QUOTA_AND_TERMINATE    = 0x0101

    kernel32 = ctypes.windll.kernel32
    job   = kernel32.CreateJobObjectW(None, None)
    hproc = kernel32.OpenProcess(PROCESS_SET_QUOTA_AND_TERMINATE, False, pid)