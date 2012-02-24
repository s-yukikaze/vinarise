import mmap
import os
import re
import vim
import os.path
from sys import version_info

class VinariseBuffer:
    __PYTHON_VAR__ = sys.version_info[:3]

    def open(self, path, is_windows):
        # init vars
        self.file = open(path, 'rb')
        self.path = path
        self.is_windows = is_windows
        fsize = os.path.getsize(self.path)
        mmap_max = 0
        if fsize > 1000000000:
            mmap_max = 1000000000

        if int(is_windows):
            self.mmap = mmap.mmap(self.file.fileno(), mmap_max,
                    None, mmap.ACCESS_COPY, 0)
        else:
            self.mmap = mmap.mmap(self.file.fileno(), mmap_max,
                    access = mmap.ACCESS_COPY, offset = 0)

    def close(self):
        self.file.close()
        self.mmap.close()

    def write(self, path):
        if path == self.path:
            # Close current file temporary.
            str = self.mmap[0:]
            is_windows = self.is_windows
            self.close()
        else:
            str = self.mmap

        write_file = open(path, 'wb')
        write_file.write(str)
        write_file.close()

        if path == self.path:
            # Re open file.
            self.open(path, is_windows)

    if __PYTHON_VAR__ < (3, 0, 0):
        # Python < 3.0.0 : mmap.mmap[] behaves like string.
        def get_byte(self, addr):
            return ord(self.mmap[int(addr)])

        def set_byte(self, addr, value):
            self.mmap[int(addr)] = chr(int(value))

        def get_bytes(self, addr, count):
            if int(count) == 0:
                return []
            return [ord(x) for x in self.mmap[int(addr) : int(addr)+int(count)-1]]
    else:
        # Python >= 3.0.0: mmap.mmap[] behaves like bytearray.
        def get_byte(self, addr):
            return self.mmap[int(addr)]

        def set_byte(self, addr, value):
            self.mmap[int(addr)] = int(value)

        def get_bytes(self, addr, count):
            if int(count) == 0:
                return []
            return [x for x in self.mmap[int(addr) : int(addr)+int(count)-1]]

    def get_percentage(self, address):
        return (int(address)*100) // (os.path.getsize(self.path) - 1)

    def get_percentage_address(self, percent):
        return (os.path.getsize(self.path) * int(percent)) // 100

    def find(self, address, str):
        return self.mmap.find(str, int(address))

    def rfind(self, address, str):
        return self.mmap.rfind(str, 0, int(address))

    def find_regexp(self, address, str):
        pattern = re.compile(str)
        m = pattern.search(self.mmap, int(address))
        if m is None:
            return -1
        else:
            return m.start()

