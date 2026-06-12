import asyncio
import sys
from datetime import datetime
from typing import Optional

from src.utils import TextFormat


class AsyncLogger:
    _queue_console: asyncio.Queue = asyncio.Queue()
    _queue_logfile: asyncio.Queue = asyncio.Queue()
    _task: Optional[asyncio.Task] = None
    _file = None
    _started = False

    @staticmethod
    def get_logger():
        return AsyncLogger()

    @staticmethod
    async def start(logfile="SEBA.log", to_console=True):
        if AsyncLogger._started:
            return

        AsyncLogger._file = open(logfile, "a") if logfile else None
        AsyncLogger._to_console = to_console
        AsyncLogger._started = True

        AsyncLogger._task = asyncio.create_task(AsyncLogger._worker())

    @staticmethod
    async def stop():
        if not AsyncLogger._started:
            return

        await AsyncLogger._queue_console.put(None)
        await AsyncLogger._queue_logfile.put(None)

        if AsyncLogger._task:
            await AsyncLogger._task

        if AsyncLogger._file:
            AsyncLogger._file.close()

        AsyncLogger._started = False

    @staticmethod
    def debug(msg): AsyncLogger._enqueue("DEBUG", msg)
    @staticmethod
    def info(msg): AsyncLogger._enqueue("INFO", msg)
    @staticmethod
    def warning(msg): AsyncLogger._enqueue("WARNING", msg)
    @staticmethod
    def error(msg): AsyncLogger._enqueue("ERROR", msg)

    @staticmethod
    def _enqueue(level, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        record_logfile = f"[{ts}] [{level}] {msg}"

        if level == "DEBUG":
            record_console = f"[{ts}] {TextFormat.format(f"[{level}]", fmt="Bg")}\t{msg}"
        if level == "INFO":
            record_console = f"[{ts}] {TextFormat.format(f"[{level}]", fmt="Bb")}\t{msg}"
        if level == "WARNING":
            record_console = f"[{ts}] {TextFormat.format(f"[{level}]", fmt="By")}\t{msg}"
        if level == "ERROR":
            record_console = f"[{ts}] {TextFormat.format(f"[{level}]", fmt="Br")}\t{msg}"

        try:
            AsyncLogger._queue_console.put_nowait(record_console)
            AsyncLogger._queue_logfile.put_nowait(record_logfile)
        except asyncio.QueueFull:
            pass

    @staticmethod
    async def _worker():
        while True:
            record_console = await AsyncLogger._queue_console.get()
            record_logfile = await AsyncLogger._queue_logfile.get()

            if record_console is None:
                break

            if getattr(AsyncLogger, "_to_console", True):
                print(record_console)

            if AsyncLogger._file:
                AsyncLogger._file.write(record_logfile + "\n")
                AsyncLogger._file.flush()