import cv2
import mediapipe as mp
import time
import math
import collections

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=5, refine_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5)
drawing_spec = mp.solutions.drawing_utils.DrawingSpec(thickness=1, circle_radius=1)

def get_zone(nose_x, nose_y, width, height):
    if nose_x < width * 0.3:
        return 'LEFT'
    elif nose_x > width * 0.7:
        return 'RIGHT'
    elif nose_y < height * 0.3:
        return 'TOP'
    elif nose_y > height * 0.7:
        return 'BOTTOM'
    else:
        return 'CENTER'

def get_detailed_zone(nose_x, nose_y, width, height):
    if nose_x < width * 0.3:
        if nose_y > height * 0.7:
            return 'BL'
        elif nose_y < height * 0.3:
            return 'TL'
        else:
            return 'LEFT'
    elif nose_x > width * 0.7:
        if nose_y > height * 0.7:
            return 'BR'
        elif nose_y < height * 0.3:
            return 'TR'
        else:
            return 'RIGHT'
    else:
        if nose_y > height * 0.7:
            return 'BOTTOM'
        elif nose_y < height * 0.3:
            return 'TOP'
        else:
            return 'CENTER'

def calculate_head_direction(nose_tip, forehead):
    dx = nose_tip[0] - forehead[0]
    dy = nose_tip[1] - forehead[1]
    if abs(dx) > abs(dy):
        return 'LEFT' if dx > 0 else 'RIGHT'
    else:
        return 'DOWN' if dy > 0 else 'UP'

def get_face_landmark_points(landmarks, w, h, indices=[1, 10]):
    return [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in indices]

def distances_between_points(points1, points2):
    return [math.hypot(p1[0]-p2[0], p1[1]-p2[1]) for p1, p2 in zip(points1, points2)]

def monitor_attention():
    cap = cv2.VideoCapture(0)
    max_faces = 5
    last_away_time_list = [None] * max_faces
    look_away_duration_list = [0] * max_faces
    look_away_frequency_list = [0] * max_faces
    face_not_detected_start = None
    zone_start_times_list = [{} for _ in range(max_faces)]
    freq_zone_times_list = [collections.defaultdict(list) for _ in range(max_faces)]
    reference_landmarks_list = [None] * max_faces
    reference_cheek_iris_list = [None] * max_faces
    deviation_threshold = 30
    deviation_cheekiris_threshold = 18

    print("Press 'r' to capture reference (ideal pose). Press 'Esc' to exit.")

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty frame.")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = face_mesh.process(frame_rgb)
        current_time = time.time()
        h, w, _ = frame.shape

        if not result.multi_face_landmarks:
            if face_not_detected_start is None:
                face_not_detected_start = current_time
            elif current_time - face_not_detected_start > 3:
                cv2.putText(frame, " No Face Detected >3s", (50, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
            cv2.putText(frame, " Face not detected", (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.imshow('Attention Monitor', frame)
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
            continue
        else:
            face_not_detected_start = None

        for idx, face_landmarks in enumerate(result.multi_face_landmarks[:max_faces]):
            try:
                landmarks = face_landmarks.landmark
                nose_tip = landmarks[1]
                forehead = landmarks[10]
                nose_coords = (int(nose_tip.x * w), int(nose_tip.y * h))
                forehead_coords = (int(forehead.x * w), int(forehead.y * h))
                cheek1_coords = (int(landmarks[234].x * w), int(landmarks[234].y * h))
                cheek2_coords = (int(landmarks[454].x * w), int(landmarks[454].y * h))
                iris_left_coords = (int(landmarks[468].x * w), int(landmarks[468].y * h))
                iris_right_coords = (int(landmarks[473].x * w), int(landmarks[473].y * h))
                for pt in [nose_coords, forehead_coords, cheek1_coords, cheek2_coords, iris_left_coords, iris_right_coords]:
                    cv2.circle(frame, pt, 4, (0,150,255), -1)
                direction = calculate_head_direction(nose_coords, forehead_coords)
                zone = get_zone(nose_coords[0], nose_coords[1], w, h)
                zone_detailed = get_detailed_zone(nose_coords[0], nose_coords[1], w, h)

                key = cv2.waitKey(1) & 0xFF
                if key == ord('r'):
                    reference_landmarks_list[idx] = get_face_landmark_points(landmarks, w, h)
                    reference_cheek_iris_list[idx] = (
                        math.hypot(cheek1_coords[0]-iris_left_coords[0], cheek1_coords[1]-iris_left_coords[1]),
                        math.hypot(cheek2_coords[0]-iris_right_coords[0], cheek2_coords[1]-iris_right_coords[1])
                    )
                    cv2.putText(frame, f"Reference captured ({idx})!", (50, 400 + 25*idx), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
                    print(f"Reference landmarks and cheek-iris distances captured for face {idx}.")

                if reference_landmarks_list[idx]:
                    current_pts = get_face_landmark_points(landmarks, w, h)
                    deviations = distances_between_points(reference_landmarks_list[idx], current_pts)
                    if any(d > deviation_threshold for d in deviations):
                        cv2.putText(frame, f"Face {idx} deviated from ref!", (50, 300 + idx*20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if reference_cheek_iris_list[idx]:
                    if iris_left_coords and iris_right_coords:
                        d1 = math.hypot(cheek1_coords[0]-iris_left_coords[0], cheek1_coords[1]-iris_left_coords[1])
                        d2 = math.hypot(cheek2_coords[0]-iris_right_coords[0], cheek2_coords[1]-iris_right_coords[1])
                        rd1, rd2 = reference_cheek_iris_list[idx]
                        if abs(d1-rd1) > deviation_cheekiris_threshold or abs(d2-rd2) > deviation_cheekiris_threshold:
                            cv2.putText(frame, f"Face {idx} cheek-iris drift!", (50, 370+idx*20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 0, 255), 2)
                    else:
                        cv2.putText(frame, f"Face {idx}: Iris not found", (50, 370+idx*20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (180, 0, 255), 2)

                if zone == 'CENTER':
                    look_away_duration_list[idx] = 0
                    last_away_time_list[idx] = None
                else:
                    if last_away_time_list[idx] is None:
                        last_away_time_list[idx] = current_time
                        look_away_frequency_list[idx] += 1
                    look_away_duration_list[idx] = current_time - last_away_time_list[idx]

                if 2 < look_away_duration_list[idx] <= 5:
                    cv2.putText(frame, f"Face {idx} Looking away >2s", (50, 200 + idx*20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)
                elif look_away_duration_list[idx] > 5:
                    cv2.putText(frame, f"Face {idx} Long Look Away >5s", (50, 230 + idx*20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if zone_detailed in ['BL', 'BR', 'TR']:
                    if zone_detailed not in zone_start_times_list[idx]:
                        zone_start_times_list[idx][zone_detailed] = current_time
                    elif current_time - zone_start_times_list[idx][zone_detailed] > 3:
                        cv2.putText(frame, f"Face {idx} AOI Suspicious {zone_detailed} >3s", (50, 170 + idx*20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
                else:
                    for key_zone in list(zone_start_times_list[idx]):
                        if key_zone != zone_detailed:
                            del zone_start_times_list[idx][key_zone]

                if zone_detailed != 'CENTER':
                    freq_zone_times_list[idx][zone_detailed] = [t for t in freq_zone_times_list[idx][zone_detailed] if current_time - t <= 60]
                    freq_zone_times_list[idx][zone_detailed].append(current_time)
                    if len(freq_zone_times_list[idx][zone_detailed]) >= 5:
                        cv2.putText(frame, f"Face {idx} Frequent Glances {zone_detailed}!", (50, 260 + idx*20),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                if look_away_duration_list[idx] > 3:
                    cv2.putText(frame, f"Face {idx} Looking away too long ({int(look_away_duration_list[idx])}s)", (50, 50 + idx*30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if look_away_frequency_list[idx] >= 5:
                    cv2.putText(frame, f"Face {idx} Frequent distractions detected!", (50, 80 + idx*20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                if zone in ['LEFT', 'RIGHT', 'TOP', 'BOTTOM']:
                    cv2.putText(frame, f"Face {idx} Looking: {zone}", (50, 110 + idx*20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            except Exception:
                pass

        cv2.imshow('Attention Monitor', frame)
        key2 = cv2.waitKey(5) & 0xFF
        if key2 == 27:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    monitor_attention()
