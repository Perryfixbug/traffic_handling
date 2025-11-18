import cv2
import numpy as np
import math
import time
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort


# =========================
# 1) HOMOGRAPHY FUNCTIONS
# =========================
def pixel_to_world(px, py, H):
    """Convert pixel (px, py) → meters (x, y) using homography H."""
    p = np.array([[px, py, 1.0]]).T
    wp = H @ p
    wp /= wp[2]
    return float(wp[0]), float(wp[1])


def compute_speed(points_list, fps, min_df=5, smooth_N=3, max_speed=200):
    """Compute smoothed vehicle speed from world-coordinate history."""
    if len(points_list) < 2:
        return None

    # Find an earlier point with min_df frames difference
    idx_prev = None
    for i in range(len(points_list) - 2, -1, -1):
        if points_list[-1][2] - points_list[i][2] >= min_df:
            idx_prev = i
            break
    if idx_prev is None:
        idx_prev = len(points_list) - 2

    # Smoothing over last N segments
    start_idx = max(idx_prev, len(points_list) - smooth_N - 1)
    speeds = []

    for i in range(start_idx, len(points_list) - 1):
        x1, y1, f1 = points_list[i]
        x2, y2, f2 = points_list[i + 1]
        dt = (f2 - f1) / fps
        if dt <= 0:
            continue

        speed = math.hypot(x2 - x1, y2 - y1) / dt * 3.6
        if speed <= max_speed:
            speeds.append(speed)

    return sum(speeds) / len(speeds) if speeds else None


# =========================
# 2) HOMOGRAPHY INPUT
# =========================
pts_src = np.array([
    [675, 575],
    [1250, 575],
    [375, 1080],
    [1920, 1080]
], dtype=np.float32)

pts_dst = np.array([
    [0, 0],
    [22, 0],
    [0, 78],
    [22, 78]
], dtype=np.float32)

Hmat, _ = cv2.findHomography(pts_src, pts_dst)
print("Homography matrix:\n", Hmat)


# =========================
# 3) MODEL & TRACKER
# =========================
model = YOLO("yolov8s.pt")
tracker = DeepSort(max_age=30)


# =========================
# 4) VIDEO INPUT
# =========================
VIDEO_PATH = "traffic.mp4"
DISPLAY_SCALE = 0.6     # giảm kích thước hiển thị còn 60%

cap = cv2.VideoCapture(VIDEO_PATH)
FPS = cap.get(cv2.CAP_PROP_FPS) or 30.0

if not cap.isOpened():
    print("❌ Không mở được video:", VIDEO_PATH)
    exit()

positions = {}
frame_idx = 0


# =========================
# 5) MAIN LOOP
# =========================
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ---- YOLO DETECTION ----
    results = model(frame, verbose=False, conf=0.4)[0]

    detections = []
    for box in results.boxes:
        cls = int(box.cls[0])
        if cls in [2, 3, 5, 7]:   # car, motorcycle, bus, truck
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            detections.append(([x1, y1, x2 - x1, y2 - y1], float(box.conf[0]), cls))

    # ---- TRACKING ----
    tracks = tracker.update_tracks(detections, frame=frame)

    for tr in tracks:
        if not tr.is_confirmed():
            continue

        tid = tr.track_id
        l, t, r, b = map(int, tr.to_ltrb())
        cx, cy = (l + r) // 2, (t + b) // 2

        # Convert to world meters
        wx, wy = pixel_to_world(cx, cy, Hmat)
        positions.setdefault(tid, []).append((wx, wy, frame_idx))

        # Compute speed
        speed_kmh = compute_speed(positions[tid], FPS)

        # ---- DRAW ----
        cv2.rectangle(frame, (l, t), (r, b), (0, 255, 0), 2)
        label = f"ID:{tid}"
        if speed_kmh is not None:
            label += f" {speed_kmh:.1f} km/h"

        cv2.putText(frame, label, (l, t - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

    # ---- RESIZE FOR DISPLAY ----
    disp_frame = cv2.resize(frame, None, fx=DISPLAY_SCALE, fy=DISPLAY_SCALE)

    cv2.imshow("Speed Detection (Realtime from Video File)", disp_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    frame_idx += 1

cap.release()
cv2.destroyAllWindows()
