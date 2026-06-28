---
skill_id: db0165fa9ae8
usage_count: 1
last_used: 2026-06-16
---
# Correct struct layout — LimitFlags is at offset +16, not +44
    class JOBOBJECT_BASIC_LIMIT_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", wt.LARGE_INTEGER),
            ("PerJobUserTimeLimit",     wt.LARGE_INTEGER),
            ("LimitFlags",             wt.DWORD),
            ("MinimumWorkingSetSize",   ctypes.c_size_t),
            ("MaximumWorkingSetSize",   ctypes.c_size_t),
            ("ActiveProcessLimit",      wt.DWORD),
            ("Affinity",               ctypes.c_size_t),
            ("PriorityClass",          wt.DWORD),
            ("SchedulingClass",        wt.DWORD),
        ]

    info = JOBOBJECT_BASIC_LIMIT_INFORMATION()
    info.LimitFlags = JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
    ok = kernel32.SetInformationJobObject(job, 2, ctypes.byref(info), ctypes.sizeof(info))
    if not ok:
        raise ctypes.WinError()
    kernel32.AssignProcessToJobObject(job, hproc)
    kernel32.CloseHandle(hproc)
    return job  # keep alive — job closes (kills proc) when GC'd