# Project: Face Detection in Images

## Project Description

This Python script iterates through a folder containing images (.jpg, .png), detects faces within each image using the **Insightface** library, and compares these detected faces against a set of known "target" faces. If a match is found (based on a similarity threshold), the detected face is marked in the image, and the processed image is saved to a separate output folder.

This is useful for quickly finding images that contain specific individuals, especially when dealing with a large number of image files.

## How it Works

1.  **Initialization:**
    *   The script initializes the Insightface `FaceAnalysis` application (`app = FaceAnalysis()`) [2].
    *   It prepares the model for detection (specifying context like GPU/CPU and detection size) [2].
    *   It loads target faces from specified image paths, detects the face in each target image, and computes their L2-normalized embeddings. These are stored in a dictionary `target_embeddings` keyed by the person's label [2].
    *   Defines constants such as the path to the images folder (`IMAGES_FOLDER`), the path to the output folder (`OUTPUT_FOLDER`), and the similarity threshold (`SIMILARITY_THRESHOLD`) [2].
    *   Creates the output folder (`OUTPUT_FOLDER`) if it doesn't already exist [2].

2.  **Image Processing:**
    *   The script loops through all `.jpg` and `.png` files found within the `IMAGES_FOLDER` [2].
    *   For each image, it attempts to load it using OpenCV (`cv2.imread`) [2].
    *   The function `get_embedding_and_bbox(app, image)` is called. This function uses the initialized Insightface `app` to detect faces and retrieve their normalized embeddings (`face.normed_embedding`) and bounding boxes (`face.bbox`) [2].

3.  **Face Comparison:**
    *   For each face detected in the image, its embedding is compared with the embeddings of all target faces (`target_embeddings`) [2].
    *   The comparison is performed using cosine distance (`cosine_distance`). Since the embeddings are L2-normalized, cosine distance is calculated as `1 - np.dot(v1, v2)`. A smaller value indicates higher similarity (0 means identical) [2].
    *   If the calculated distance between a detected face and a target face is below the `SIMILARITY_THRESHOLD`, a match is determined (`found_match = True`) [2].

4.  **Annotation and Saving:**
    *   Upon finding a match, information about the match (target name, filename, distance, bounding box) is printed to the console [2].
    *   A green rectangle is drawn around the detected face in the image (`cv2.rectangle`) [2].
    *   The target's name and the distance are written above the rectangle (`cv2.putText`) [2].
    *   If at least one match was found in an image, the processed image (with markups) is saved to the `OUTPUT_FOLDER` (`cv2.imwrite`) [2].

## Requirements

*   Python 3.x
*   An installation of the **Insightface** library and its dependencies.
*   A folder (`IMAGES_FOLDER`) containing the images to be searched (.jpg, .png) [2].
*   Target images for the individuals you want to find. The script needs to be configured to load these and compute their embeddings [2].
*   The Python libraries listed below.

## Installation & Dependencies

The required Python libraries are listed in the `requirements.txt` file. Based on your `venv` contents and the code snippets, the key dependencies are:

```text
# requirements.txt
opencv-python
numpy
tqdm
insightface
