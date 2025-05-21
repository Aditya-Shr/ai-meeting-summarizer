from typing import Dict
import threading

class ProcessManager:
    _active_processes: Dict[str, bool] = {}
    _lock = threading.Lock()

    @classmethod
    def register_process(cls, process_id: str) -> None:
        """Register a new process"""
        with cls._lock:
            cls._active_processes[process_id] = True

    @classmethod
    def cancel_process(cls, process_id: str) -> bool:
        """Cancel a process if it exists"""
        with cls._lock:
            if process_id in cls._active_processes:
                cls._active_processes[process_id] = False
                return True
            return False

    @classmethod
    def is_cancelled(cls, process_id: str) -> bool:
        """Check if a process is cancelled"""
        with cls._lock:
            return process_id in cls._active_processes and not cls._active_processes[process_id]

    @classmethod
    def remove_process(cls, process_id: str) -> None:
        """Remove a process from tracking"""
        with cls._lock:
            cls._active_processes.pop(process_id, None) 