from __future__ import annotations

import time
from threading import Lock
from typing import Generator, Optional, Tuple

import cv2
import numpy as np


class CameraError(RuntimeError):
    """Raised when camera operations fail."""


class USBCamera:
    """Simple wrapper around cv2.VideoCapture for USB cameras."""

    def __init__(
        self,
        device_index: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None,
        backend: Optional[int] = None,
    ) -> None:
        self.device_index = device_index
        self.backend = backend
        self._requested_resolution: Optional[Tuple[int, int]] = (
            (width, height) if width and height else None
        )
        self._cap: Optional[cv2.VideoCapture] = None
        self._lock = Lock()

    def __enter__(self) -> "USBCamera":
        self.open()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def open(self) -> None:
        with self._lock:
            if self._cap and self._cap.isOpened():
                return

            cap = (
                cv2.VideoCapture(self.device_index, self.backend)
                if self.backend is not None
                else cv2.VideoCapture(self.device_index)
            )

            if not cap.isOpened():
                cap.release()
                raise CameraError(f"Unable to open camera at index {self.device_index}")

            if self._requested_resolution:
                width, height = self._requested_resolution
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(width))
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(height))

            self._cap = cap

    def close(self) -> None:
        with self._lock:
            if self._cap is None:
                return
            if self._cap.isOpened():
                self._cap.release()
            self._cap = None

    def is_open(self) -> bool:
        return bool(self._cap and self._cap.isOpened())

    def _require_open(self) -> cv2.VideoCapture:
        if not self._cap or not self._cap.isOpened():
            raise CameraError("Camera is not open. Call open() first.")
        return self._cap

    def set_resolution(self, width: int, height: int) -> None:
        with self._lock:
            self._requested_resolution = (width, height)
            if self._cap and self._cap.isOpened():
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, float(width))
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, float(height))

    def get_resolution(self) -> Optional[Tuple[int, int]]:
        if not self.is_open():
            return self._requested_resolution
        cap = self._require_open()
        return (
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )

    def read(self, timeout: Optional[float] = 2.0) -> np.ndarray:
        cap = self._require_open()
        start = time.perf_counter()

        while True:
            ok, frame = cap.read()
            if ok:
                return frame
            if timeout is not None and (time.perf_counter() - start) >= timeout:
                raise CameraError("Timed out waiting for frame")
            time.sleep(0.01)

    def snapshot(self, convert_rgb: bool = True, timeout: Optional[float] = 2.0) -> np.ndarray:
        frame = self.read(timeout=timeout)
        if convert_rgb:
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    def stream(
        self, interval: float = 0.0, timeout: Optional[float] = 2.0
    ) -> Generator[np.ndarray, None, None]:
        while True:
            yield self.snapshot(convert_rgb=False, timeout=timeout)
            if interval > 0:
                time.sleep(interval)

    def __del__(self) -> None:
        try:
            self.close()
        except Exception:
            pass
