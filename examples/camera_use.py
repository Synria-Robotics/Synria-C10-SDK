# Copyright (c) 2026 Synria Robotics Co., Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.
#
# Author: Synria Robotics Team
# Website: https://synriarobotics.ai

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
