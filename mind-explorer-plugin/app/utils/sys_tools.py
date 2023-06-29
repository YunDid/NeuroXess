#!/usr/bin/python  
# -*- coding:utf-8 _*-
import time
import win32api
import win32con
import win32process


def bind_cpu(cpu_id: int):
    pid = win32api.GetCurrentProcess()
    win32process.SetProcessAffinityMask(pid, cpu_id)
    handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, win32api.GetCurrentProcessId())
    win32process.SetPriorityClass(handle, win32process.REALTIME_PRIORITY_CLASS)


if __name__ == '__main__':
    bind_cpu(0x0010)
    print(win32api.GetSystemInfo())
    print(win32api.GetCurrentProcessId())
    time.sleep(100)