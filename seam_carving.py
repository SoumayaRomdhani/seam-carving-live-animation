import numpy as np
import cv2


# ----------------------------
# Energy map (fast)
# ----------------------------
def to_gray(img_rgb: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)


def energy_map(img_rgb: np.ndarray) -> np.ndarray:
    """
    Energy = |Sobel_x| + |Sobel_y|
    High energy = important pixels (edges/details)
    """
    gray = to_gray(img_rgb)
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    return np.abs(gx) + np.abs(gy)


# ----------------------------
# Find minimum vertical seam (DP)
# ----------------------------
def find_vertical_seam(energy: np.ndarray) -> np.ndarray:
    """
    energy: (H, W)
    return seam: array length H (seam[i] = column index in row i)
    """
    H, W = energy.shape
    M = energy.copy()
    backtrack = np.zeros((H, W), dtype=np.int32)

    for i in range(1, H):
        prev = M[i - 1]

        left = np.hstack([np.inf, prev[:-1]])
        up = prev
        right = np.hstack([prev[1:], np.inf])

        choices = np.vstack([left, up, right])  # (3, W)
        idx = np.argmin(choices, axis=0)

        M[i] += choices[idx, np.arange(W)]
        backtrack[i] = idx - 1  # -1 left, 0 up, +1 right

    seam = np.zeros(H, dtype=np.int32)
    j = np.argmin(M[-1])
    seam[-1] = j

    for i in range(H - 2, -1, -1):
        j = j + backtrack[i + 1, j]
        seam[i] = j

    return seam


# ----------------------------
# Remove seam
# ----------------------------
def remove_vertical_seam(img_rgb: np.ndarray, seam: np.ndarray) -> np.ndarray:
    """
    Remove 1 vertical seam from image (H,W,3) -> (H,W-1,3)
    """
    H, W, C = img_rgb.shape
    mask = np.ones((H, W), dtype=bool)
    mask[np.arange(H), seam] = False
    out = img_rgb[mask].reshape(H, W - 1, C)
    return out


# ----------------------------
# Visualization: overlay seam
# ----------------------------
def overlay_seam(img_rgb: np.ndarray, seam: np.ndarray) -> np.ndarray:
    """
    Draw seam pixels in RED
    """
    out = img_rgb.copy()
    H = out.shape[0]
    out[np.arange(H), seam] = [255, 0, 0]
    return out


# ----------------------------
# Generators (LIVE animation)
# ----------------------------
def carve_vertical_generator(img_rgb: np.ndarray, k: int):
    """
    Yields step-by-step for live animation.
    yield (step, current_img, energy, seam_overlay_img)
    """
    cur = img_rgb.copy()

    for step in range(1, k + 1):
        e = energy_map(cur)
        seam = find_vertical_seam(e)
        seam_img = overlay_seam(cur, seam)
        cur = remove_vertical_seam(cur, seam)

        yield step, cur, e, seam_img


def carve_horizontal_generator(img_rgb: np.ndarray, k: int):
    """
    Same but for horizontal carving using transpose trick.
    """
    trans = np.transpose(img_rgb, (1, 0, 2))  # (W,H,3)

    for step, cur_t, e_t, seam_img_t in carve_vertical_generator(trans, k):
        # transpose back
        cur = np.transpose(cur_t, (1, 0, 2))
        e = e_t.T
        seam_img = np.transpose(seam_img_t, (1, 0, 2))
        yield step, cur, e, seam_img
