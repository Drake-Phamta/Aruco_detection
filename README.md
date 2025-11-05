# Aruco_detection

Aruco_detection is a project for detecting and processing ArUco markers using computer vision techniques. ArUco markers are binary square fiducial markers that are widely used in robotics, computer vision, and augmented reality for camera pose estimation and object tracking.

## Features

- Detect ArUco markers in images or video streams.
- Estimate the pose (position and orientation) of detected markers.
- Visualize detected markers with bounding boxes and axes.
- Support for different ArUco dictionaries.
- Customizable minimum detection confidence threshold.
- Real-time detection with webcam or video file input.

## Installation

1. **Clone this repository**
   ```bash
   git clone https://github.com/Drake-Phamta/Aruco_detection.git
   cd Aruco_detection
   ```

2. **Install dependencies**

   Most likely, this project uses Python with OpenCV (`opencv-contrib-python`) and possibly other libraries. Install dependencies with:

   ```bash
   pip install -r requirements.txt
   ```

   Or manually, for common dependencies:
   ```bash
   pip install opencv-contrib-python numpy
   ```

## Usage

Assuming the main script is called `aruco_detection.py`:

```bash
python aruco_detection.py --input [input_source] --dict [aruco_dict] --show-axes
```

- `--input`: Path to a video file or '0' for webcam.
- `--dict`: ArUco dictionary type (e.g., DICT_6X6_250).
- `--show-axes`: (Optional) Display axes on detected markers.

Example:
```bash
python aruco_detection.py --input 0 --dict DICT_6X6_250 --show-axes
```

## Project Structure

```
Aruco_detection/
├── README.md
├── requirements.txt
├── aruco_detection.py
└── ... (other scripts/modules)
```

## Supported ArUco Dictionaries

- DICT_4X4_50
- DICT_5X5_100
- DICT_6X6_250
- DICT_7X7_1000
- ...and more (see OpenCV ArUco module documentation)

## References

- [OpenCV ArUco Module Documentation](https://docs.opencv.org/master/d5/dae/tutorial_aruco_detection.html)
- [ArUco: a minimal library for Augmented Reality applications based on OpenCv](https://www.uco.es/investiga/grupos/ava/node/26)

## License

This project is licensed under the MIT License.

---

For questions or contributions, feel free to open an issue or submit a pull request!