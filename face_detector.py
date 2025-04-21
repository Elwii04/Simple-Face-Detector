import os
import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis
from tqdm import tqdm  # Added progress bar support

#os.environ.pop('CUDA_PATH', None)  # Remove CUDA_PATH if present

# ----------------------------------------------------
# CONFIG
# ----------------------------------------------------
TARGET_IMAGES = {
    "PersonA": "name1.png",
    "PersonB": "name2.png"
    # Add more as needed: "Label": "filename.jpg"
}

IMAGES_FOLDER = "images"        # Folder containing images to check
OUTPUT_FOLDER = "output"        # Folder for saving annotated matches
SIMILARITY_THRESHOLD = 0.65     # Adjust to control match strictness
# ----------------------------------------------------

def get_embedding_and_bbox(app, img):
    """Detect faces in an image, return (embedding, bbox) for each face."""
    faces = app.get(img)
    results = []
    for face in faces:
        emb = face.normed_embedding  # L2-normalized embedding
        bbox = face.bbox  # [x1, y1, x2, y2]
        results.append((emb, bbox))
    return results

def cosine_distance(v1, v2):
    """Compute 1 - cosine_similarity (0 = same, 2 = opposite)."""
    return 1 - np.dot(v1, v2)  # embeddings are normalized

def main():
    # 1. Initialize FaceAnalysis (GPU: ctx_id=0, CPU: ctx_id=-1)
    app = FaceAnalysis()
    
    app.prepare(ctx_id=0, det_size=(640, 640))
    
    # 2. Load each target face and compute its embedding
    target_embeddings = {}  # { "PersonA": embedding, "PersonB": embedding, ... }
    for label, img_path in tqdm(TARGET_IMAGES.items(), desc="Loading target faces"):
        img = cv2.imread(img_path)
        if img is None:
            print(f"Could not read target image: {img_path}")
            continue
        results = get_embedding_and_bbox(app, img)
        if not results:
            print(f"No face detected in target image: {img_path}")
            continue
        target_embeddings[label] = results[0][0]  # use the first face's embedding

    if not target_embeddings:
        print("No valid target faces found. Exiting.")
        return

    # 3. Create output folder if it doesn't exist
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # 4. Process each image in the input folder
    image_files = [f for f in os.listdir(IMAGES_FOLDER) if f.lower().endswith((".jpg", ".png"))]
    for filename in tqdm(image_files, desc="Processing images"):
        img_path = os.path.join(IMAGES_FOLDER, filename)
        image = cv2.imread(img_path)
        if image is None:
            continue
        
        faces = get_embedding_and_bbox(app, image)
        found_match = False
        
        # Process detected faces in the image
        for (emb, bbox) in tqdm(faces, desc="Processing faces", leave=False):
            # Compare with each target face
            for label, target_emb in tqdm(target_embeddings.items(), desc="Comparing with targets", leave=False):
                dist = cosine_distance(target_emb, emb)
                if dist < SIMILARITY_THRESHOLD:
                    # Found a match
                    found_match = True
                    print(f"Match for {label} in {filename} | Distance: {dist:.3f} | BBox: {bbox}")
                    
                    # Draw bounding box and label
                    x1, y1, x2, y2 = [int(v) for v in bbox]
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(image, f"{label}:{dist:.3f}", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Save the annotated image if we found any match
        if found_match:
            out_path = os.path.join(OUTPUT_FOLDER, filename)
            cv2.imwrite(out_path, image)

if __name__ == "__main__":
    main()
