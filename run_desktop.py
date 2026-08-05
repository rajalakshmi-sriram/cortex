#!/usr/bin/env python
"""
Entry point for the packaged Cortex desktop app.

This is what the Tauri desktop shell spawns as a child process (as a
PyInstaller-built standalone binary, no separate Python install required on
the user's machine). Binds to 127.0.0.1 only - this is a local desktop app,
not a server other machines on the network should be able to reach - and
runs without the Flask dev reloader, which forks a second process and would
break inside a frozen executable.

Boot resiliency: if Tauri sets CORTEX_PARENT_PID, a background thread
watches that PID and exits this process the moment it disappears. Without
this, a force-quit or crash of the Tauri app (which doesn't always give
child processes a chance to be told to shut down) could leave this backend
running forever, holding its port and silently serving nothing anyone can
see - and then blocking the *next* launch from starting its own backend
cleanly. This guarantees a clean slate on every relaunch regardless of how
the previous run ended.
"""

import os
import sys
import threading
import time
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

os.environ.setdefault('FLASK_ENV', 'production')

from app.app import create_app
from app.logger import logger


def _pid_alive(pid: int) -> bool:
    if sys.platform == 'win32':
        import ctypes
        PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not handle:
            return False
        ctypes.windll.kernel32.CloseHandle(handle)
        return True
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but is owned by someone else - still alive
        return True


def _watch_parent(pid: int, poll_seconds: float = 2.0):
    while True:
        time.sleep(poll_seconds)
        if not _pid_alive(pid):
            logger.info(f"Parent process {pid} is gone - shutting down backend")
            os._exit(0)


def main():
    port = int(os.getenv('PORT', 5050))

    parent_pid = os.getenv('CORTEX_PARENT_PID')
    if parent_pid:
        threading.Thread(target=_watch_parent, args=(int(parent_pid),), daemon=True).start()

    app = create_app()

    logger.info(f"Cortex desktop backend starting on 127.0.0.1:{port}")
    try:
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
