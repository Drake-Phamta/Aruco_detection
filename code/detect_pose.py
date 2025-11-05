import pyrealsense2 as rs
import numpy as np
import cv2

# ==============================================================================
# --- CẤU HÌNH ---
# ==============================================================================
MARKER_REAL_SIZE_M = 0.048

# --- Cấu hình bộ lọc EMA ---
ALPHA = 0.15 

# --- Offset từ Marker đến tâm hộp (đơn vị mét) ---
OFFSET_X_M = 0.0
OFFSET_Y_M = 0.10
OFFSET_Z_M = -0.04
# ==============================================================================


# --- CẤU HÌNH CAMERA VÀ ARUCO ---
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_250)


# --- BƯỚC 1: KHỞI TẠO PIPELINE VÀ CĂN CHỈNH (ALIGNMENT) ---
print("Đang khởi tạo pipeline của RealSense...")
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, CAMERA_WIDTH, CAMERA_HEIGHT, rs.format.z16, CAMERA_FPS)
config.enable_stream(rs.stream.color, CAMERA_WIDTH, CAMERA_HEIGHT, rs.format.bgr8, CAMERA_FPS)
profile = pipeline.start(config)
align_to = rs.stream.color
align = rs.align(align_to)
color_intrinsics = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()
camera_matrix = np.array([[color_intrinsics.fx, 0, color_intrinsics.ppx], [0, color_intrinsics.fy, color_intrinsics.ppy], [0, 0, 1]], dtype=np.float32)
dist_coeffs = np.array(color_intrinsics.coeffs, dtype=np.float32)
print("✅ Đã lấy thông số hiệu chỉnh tự động từ Camera RealSense.")


# --- BƯỚC 2: KHỞI TẠO ARUCO DETECTOR VÀ CÁC BIẾN ---
parameters = cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(ARUCO_DICT, parameters)
smoothed_pos = None # Biến cho bộ lọc EMA

print("✅ Camera RealSense đã sẵn sàng.")
print("ℹ️  Nhấn 'q' trên cửa sổ video để thoát.")


# --- BƯỚC 3: BẮT ĐẦU VÒNG LẶP XỬ LÝ LIVE ---
try:
    while True:
        frames = pipeline.wait_for_frames()
        aligned_frames = align.process(frames)
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()
        
        if not aligned_depth_frame or not color_frame:
            continue

        frame = np.asanyarray(color_frame.get_data())
        corners, ids, rejected = detector.detectMarkers(frame)
        
        if ids is not None:
            rvecs, _, _ = cv2.aruco.estimatePoseSingleMarkers(corners, MARKER_REAL_SIZE_M, camera_matrix, dist_coeffs)

            for i in range(len(ids)):
                # Lấy tọa độ (X,Y,Z) của marker từ cảm biến độ sâu
                c = corners[i][0]
                center_pixel = (int(c[:, 0].mean()), int(c[:, 1].mean()))
                depth_m = aligned_depth_frame.get_distance(center_pixel[0], center_pixel[1])

                if depth_m > 0:
                    tvec_marker_to_cam = np.array(rs.rs2_deproject_pixel_to_point(color_intrinsics, center_pixel, depth_m)).reshape(1,3)
                    
                    cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, rvecs[i], tvec_marker_to_cam, 0.05)
                    
                    # --- TÍNH TOÁN VỊ TRÍ TÂM HỘP SO VỚI CAMERA ---
                    R_marker_to_cam, _ = cv2.Rodrigues(rvecs[i])
                    offset_in_marker_frame = np.array([[OFFSET_X_M], [OFFSET_Y_M], [OFFSET_Z_M]])
                    
                    # Tính vị trí tâm hộp (dữ liệu thô)
                    raw_pos_in_cam = tvec_marker_to_cam.T + (R_marker_to_cam @ offset_in_marker_frame)
                    
                    # Áp dụng bộ lọc EMA
                    if smoothed_pos is None:
                        smoothed_pos = raw_pos_in_cam
                    else:
                        smoothed_pos = ALPHA * raw_pos_in_cam + (1 - ALPHA) * smoothed_pos
                    
                    pos_x, pos_y, pos_z = smoothed_pos.flatten()
                    
                    # Hiển thị tọa độ của tâm hộp SO VỚI CAMERA
                    cv2.putText(frame, "Bin Center Pos (vs Cam):", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, f"X: {pos_x:.3f} m", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, f"Y: {pos_y:.3f} m", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    cv2.putText(frame, f"Z: {pos_z:.3f} m", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                    
                     # Tính khoảng cách từ camera đến TÂM HỘP
                    distance_from_cam = np.linalg.norm(smoothed_pos)
                    # Hiển thị khoảng cách lên màn hình
                    cv2.putText(frame, f"Distance from Cam: {distance_from_cam:.2f} m", (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                    
                    # In cả tọa độ và khoảng cách ra terminal
                    print(f"Bin Center Pos (vs Cam): ({pos_x:.3f}, {pos_y:.3f}, {pos_z:.3f}) m | Distance: {distance_from_cam:.2f} m")
                    
                    # Vẽ điểm tâm hộp
                    tvec_bin_center_in_cam = smoothed_pos
                    (point_2D, _) = cv2.projectPoints(tvec_bin_center_in_cam, np.zeros((3,1)), np.zeros((3,1)), camera_matrix, dist_coeffs)
                    p_x, p_y = int(point_2D[0][0][0]), int(point_2D[0][0][1])
                    cv2.circle(frame, (p_x, p_y), 5, (0, 255, 255), -1)

        cv2.imshow("Live ArUco Detection - Direct Camera Coordinates", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
finally:
    print("\nĐang dừng pipeline...")
    pipeline.stop()
    cv2.destroyAllWindows()