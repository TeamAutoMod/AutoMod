import os
import asyncio
import subprocess
from subprocess import Popen



async def run(cmd):
    _popen = Popen(cmd, cwd=os.getcwd(), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while _popen.poll() is None:
        await asyncio.sleep(1)
    output, error = _popen.communicate()
    return _popen.returncode, output.decode("utf-8").strip(), error.decode("utf-8").strip()