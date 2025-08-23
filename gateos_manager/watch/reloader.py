"""Environment manifest directory watcher for hot reload (optional)."""
from __future__ import annotations

import os
from pathlib import Path
from threading import Thread
from typing import Callable

try:  # pragma: no cover - optional import path
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:  # pragma: no cover
    Observer = None  # type: ignore
    FileSystemEventHandler = object  # type: ignore


class _Handler(FileSystemEventHandler):  # type: ignore
    def __init__(self, callback: Callable[[], None]) -> None:
        self._callback = callback

    def on_any_event(self, event):  # pragma: no cover - integration tested
        if event.is_directory:
            return
        if event.src_path.endswith(('.yaml', '.yml')):
            self._callback()


def start_watch(path: Path, callback: Callable[[], None]) -> Thread | None:
    if Observer is None:
        return None
    observer = Observer()
    handler = _Handler(callback)
    observer.schedule(handler, str(path), recursive=False)
    observer_thread = Thread(target=observer.start, daemon=True)
    observer_thread.start()
    return observer_thread
