import os
import sys
import cv2

# -----------------------------------------------------------------------------
# Drawing globals
drawing     = False
start_point = ()
end_point   = ()
boxes       = []  # List of final boxes (x1, y1, x2, y2)
# -----------------------------------------------------------------------------

def draw_rectangle(event, x, y, flags, param):
    global drawing, start_point, end_point, boxes
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
        end_point   = (x, y)
    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        end_point = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        boxes.append((start_point, end_point))

# -----------------------------------------------------------------------------
def annotate_image(image_path: str, class_id: int = 0):
    global boxes, drawing, start_point, end_point
    boxes = []

    img = cv2.imread(image_path)
    if img is None:
        print(f"❌ Cannot read image: {image_path}")
        return

    clone = img.copy()
    cv2.namedWindow("Annotate", cv2.WINDOW_GUI_NORMAL)  # Better performance
    cv2.setMouseCallback("Annotate", draw_rectangle)

    instructions = "Draw boxes → [s]=save  [r]=reset  [Esc]=exit"

    while True:
        temp = clone.copy()

        # Instructions
        cv2.putText(temp, instructions, (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

        # Draw saved boxes in RED
        for (p1, p2) in boxes:
            cv2.rectangle(temp, p1, p2, (0, 0, 255), 2)

        # Draw current box (YELLOW)
        if drawing:
            cv2.rectangle(temp, start_point, end_point, (0, 255, 255), 1)

        cv2.imshow("Annotate", temp)
        key = cv2.waitKey(16) & 0xFF  # ~60 FPS (1000ms/16ms = 60fps)

        if key == ord('s') and boxes:
            save_annotations(image_path, boxes, img.shape, class_id)
            break
        elif key == ord('r'):
            boxes.clear()
        elif key == 27:  # ESC
            break

    cv2.destroyAllWindows()


# -----------------------------------------------------------------------------
def save_annotations(image_path, boxes, shape, class_id):
    h, w = shape[:2]

    rel_path = os.path.relpath(image_path, os.path.join("data_collection", "collected"))
    label_path = os.path.join("data_collection", "labels",
                              os.path.splitext(rel_path)[0] + ".txt")
    os.makedirs(os.path.dirname(label_path), exist_ok=True)

    with open(label_path, "w") as f:
        for (x1, y1), (x2, y2) in boxes:
            x1, x2 = sorted([x1, x2])
            y1, y2 = sorted([y1, y2])

            cx = ((x1 + x2) / 2) / w
            cy = ((y1 + y2) / 2) / h
            bw = abs(x2 - x1) / w
            bh = abs(y2 - y1) / h

            f.write(f"{class_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")

    print(f"✅ Saved {len(boxes)} annotations → {label_path}")

# -----------------------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python data_labeler.py <image_path> [class_id]")
        sys.exit(0)

    img_path = sys.argv[1]
    cls_id   = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    annotate_image(img_path, cls_id)
