"""Camera preview example."""
import cv2

from synria_cam import USBCamera, CameraError


def main() -> None:
    try:
        # Use device_index=1 for the external C10 camera; CAP_DSHOW improves Windows compatibility
        with USBCamera(device_index=1, width=640, height=480, backend=cv2.CAP_DSHOW) as cam:
            for frame in cam.stream(interval=0.01):
                cv2.imshow("USB Camera", frame)

                # Break when user presses q or closes the window (X button)
                key = cv2.waitKey(1) & 0xFF
                window_closed = cv2.getWindowProperty("USB Camera", cv2.WND_PROP_VISIBLE) < 1
                if key == ord("q") or window_closed:
                    break
    except CameraError as exc:
        print(f"Camera error: {exc}")
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
