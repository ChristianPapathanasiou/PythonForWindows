import ctypes

import windows
from windows import winproxy
from windows.generated_def import windef
from windows.winobject.process import WinUnicodeString
from windows.generated_def.winstructs import *

class EPUBLIC_OBJECT_TYPE_INFORMATION(ctypes.Structure):
    _fields_ = windows.utils.transform_ctypes_fields(PUBLIC_OBJECT_TYPE_INFORMATION, {"TypeName": windows.winobject.process.WinUnicodeString})


class Handle(SYSTEM_HANDLE):
    """A handle of the system"""
    @windows.utils.fixedpropety
    def process(self):
        """The process possessing the handle

        :type: :class:`WinProcess <windows.winobject.process.WinProcess>`"""
        "TODO: something smart ? :D"
        return [p for p in windows.system.processes if p.pid == self.dwProcessId][0]

    @windows.utils.fixedpropety
    def name(self):
        """The name of the handle

        :type: :class:`str`"""
        return self._get_object_name()

    @windows.utils.fixedpropety
    def type(self):
        """The type of the handle

        :type: :class:`str`"""
        return self._get_object_type()

    def _get_object_name(self):
        lh = self.local_handle
        size_needed = DWORD()
        yyy = ctypes.c_buffer(0x1000)
        size_needed = DWORD()
        winproxy.NtQueryObject(lh, ObjectNameInformation, ctypes.byref(yyy), ctypes.sizeof(yyy), ctypes.byref(size_needed))
        return WinUnicodeString.from_buffer_copy(yyy[:size_needed.value]).str

    def _get_object_type(self):
        lh = self.local_handle
        xxx = EPUBLIC_OBJECT_TYPE_INFORMATION()
        size_needed = DWORD()
        try:
            winproxy.NtQueryObject(lh, ObjectTypeInformation, ctypes.byref(xxx), ctypes.sizeof(xxx), ctypes.byref(size_needed))
        except WindowsError as e:
            if e.code != STATUS_INFO_LENGTH_MISMATCH:
                print("ERROR WITH {0:x}".format(lh))
                raise
            size = size_needed.value
            buffer = ctypes.c_buffer(size)
            winproxy.NtQueryObject(lh, ObjectTypeInformation, buffer, size, ctypes.byref(size_needed))
            xxx = EPUBLIC_OBJECT_TYPE_INFORMATION.from_buffer_copy(buffer)
        return xxx.TypeName.str

    @windows.utils.fixedpropety
    def local_handle(self):
        """A local copy of the handle, acquired with ``DuplicateHandle``

        :type: :class:`int`"""
        if self.dwProcessId == windows.current_process.pid:
            return self.wValue
        res = HANDLE()
        winproxy.DuplicateHandle(self.process.handle, self.wValue, windows.current_process.handle, ctypes.byref(res), dwOptions=DUPLICATE_SAME_ACCESS)
        return res.value

    def __repr__(self):
        return "<{0} value=<0x{1:x}> in process pid={2}>".format(type(self).__name__, self.wValue, self.dwProcessId)

    def __del__(self):
        if self.dwProcessId == windows.current_process.pid:
            return
        if hasattr(self, "_local_handle"):
            return winproxy.CloseHandle(self._local_handle)


def enumerate_handles():
    size_needed = ULONG()
    size = 0x1000
    buffer = ctypes.c_buffer(size)

    try:
        winproxy.NtQuerySystemInformation(16, buffer, size, ReturnLength=ctypes.byref(size_needed))
    except WindowsError as e:
        pass

    size = size_needed.value + 0x1000
    buffer = ctypes.c_buffer(size)
    winproxy.NtQuerySystemInformation(16, buffer, size, ReturnLength=ctypes.byref(size_needed))
    x = SYSTEM_HANDLE_INFORMATION.from_buffer(buffer)
    class _GENERATED_SYSTEM_HANDLE_INFORMATION(ctypes.Structure):
        _fields_ = [
            ("HandleCount", ULONG),
            ("Handles", Handle * x.HandleCount),
        ]
    return list(_GENERATED_SYSTEM_HANDLE_INFORMATION.from_buffer_copy(buffer[:size_needed.value]).Handles)

