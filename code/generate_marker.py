import cv2
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# --- TÙY CHỈNH THÔNG SỐ MARKER ---
ARUCO_DICT = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_250)
MARKER_ID = 33
IMAGE_SIZE = 472  # 4x4 cm ở 300 DPI

# --- TẠO MARKER ---
print(f"Đang tạo ArUco marker với từ điển DICT_5X5_250 và ID={MARKER_ID}")  

tag = np.zeros((IMAGE_SIZE, IMAGE_SIZE, 1), dtype="uint8")
cv2.aruco.generateImageMarker(ARUCO_DICT, MARKER_ID, IMAGE_SIZE, tag, 1)

file_name = f"aruco_marker_id_{MARKER_ID}.png"
cv2.imwrite(file_name, tag)
print(f"Đã lưu marker PNG: {file_name}")

# --- TẠO PDF KHỔ A4 ---
pdf_name = f"aruco_marker_id_{MARKER_ID}.pdf"

# Kích thước A4 (đơn vị: point, 1 point = 1/72 inch)
a4_width, a4_height = A4

# 4cm = 40mm = 40 / 25.4 inch ≈ 1.5748 inch
marker_size_inch = 40 / 25.4
marker_size_pt = marker_size_inch * 72  # quy đổi ra point cho PDF

# Tính vị trí giữa trang
x_center = (a4_width - marker_size_pt) / 2
y_center = (a4_height - marker_size_pt) / 2

# Tạo file PDF
c = canvas.Canvas(pdf_name, pagesize=A4)

# Chèn ảnh vào giữa trang
img = ImageReader(file_name)
c.drawImage(img, x_center, y_center, marker_size_pt, marker_size_pt)

# (Tùy chọn) ghi ID hoặc chú thích
# c.setFont("Helvetica", 10)
# c.drawCentredString(a4_width / 2, y_center - 20, f"Aruco ID {MARKER_ID} - 4x4cm")

# Lưu PDF
c.showPage()
c.save()

print(f"✅ Đã tạo PDF A4: {pdf_name}")
