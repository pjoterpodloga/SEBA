import sys
import threading
import queue
from datetime import datetime
from typing import Optional
import subprocess

from seba.utils import TextFormat


class AsyncLogger:
    _queue: queue.Queue = queue.Queue()
    _thread: Optional[threading.Thread] = None
    _file = None
    _started = False
    _to_console = True
    _stdout_lock = threading.Lock()

    @staticmethod
    def start(logfile="SEBA_$ts.log", to_console=True, directory="logs"):
        if AsyncLogger._started:
            return

        ts = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

        subprocess.run(["mkdir", "-p", directory], stdout=subprocess.DEVNULL)

        if directory.endswith("/"):
            directory = directory[:-1]

        logfile = f"{directory}/{logfile.replace('$ts', ts)}"

        AsyncLogger._file = open(logfile, "a") if logfile else None
        AsyncLogger._to_console = to_console
        AsyncLogger._started = True

        AsyncLogger._thread = threading.Thread(target=AsyncLogger._worker, daemon=True)
        AsyncLogger._thread.start()

    @staticmethod
    def stop():
        if not AsyncLogger._started:
            return

        AsyncLogger._queue.put(None)

        if AsyncLogger._thread:
            AsyncLogger._thread.join()

        if AsyncLogger._file:
            AsyncLogger._file.close()

        AsyncLogger._started = False

    # ---- API ----
    @staticmethod
    def debug(msg): AsyncLogger._enqueue("DEBUG", msg)
    @staticmethod
    def info(msg): AsyncLogger._enqueue("INFO", msg)
    @staticmethod
    def warning(msg): AsyncLogger._enqueue("WARNING", msg)
    @staticmethod
    def error(msg): AsyncLogger._enqueue("ERROR", msg)

    @staticmethod
    def progress(msg):
        """Inline output (bez newline, do progress bara)"""
        AsyncLogger._enqueue("INFO", msg, inline=True)

    # ---- internals ----
    @staticmethod
    def _enqueue(level, msg, inline=False):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_logfile = f"[{ts}] [{level}] {msg}"

        if level == "DEBUG":
            prefix = TextFormat.format(f"[{level}]", fmt="Bg")
        elif level == "INFO":
            prefix = TextFormat.format(f"[{level}]", fmt="Bb")
        elif level == "WARNING":
            prefix = TextFormat.format(f"[{level}]", fmt="By")
        elif level == "ERROR":
            prefix = TextFormat.format(f"[{level}]", fmt="Br")
        else:
            prefix = f"[{level}]"

        record_console = f"[{ts}] {prefix}\t{msg}"

        try:
            AsyncLogger._queue.put_nowait((record_console, record_logfile, inline))
        except queue.Full:
            pass

    @staticmethod
    def raw(msg: str):
        if getattr(AsyncLogger, "_to_console", True):
            sys.stdout.write(msg)
            sys.stdout.flush()
            
    @staticmethod
    def _worker():
        while True:
            item = AsyncLogger._queue.get()

            if item is None:
                break

            record_console, record_logfile, inline = item

            with AsyncLogger._stdout_lock:
                if AsyncLogger._to_console:
                    if inline:
                        sys.stdout.write(record_console)
                        sys.stdout.flush()
                    else:
                        print(record_console)

                if AsyncLogger._file:
                    AsyncLogger._file.write(record_logfile + "\n")
                    AsyncLogger._file.flush()