# 🎞 Seam Carving Live Animation — Content-Aware Image Resizing (Streamlit)

This project is an interactive **Streamlit web app** that demonstrates **Seam Carving**, a famous technique for **content-aware image resizing**.  
Unlike naive resizing (stretching/shrinking), Seam Carving removes *low-energy* pixel paths (**seams**) while preserving important objects in the image.

---

## 🎯 Objective

Resize an image **without destroying the important content** (faces, objects, edges).  
Visualize the algorithm **step-by-step** with:

- **Original image**
- **Naive resizing** (normal browser resizing)
- **Content-aware resized image** (seam carving)
- **Energy map + seam overlay**

---

## ✂️ What is Seam Carving?

Seam Carving removes **one seam at a time**:

- A **seam** is a connected path of pixels from:
  - **top → bottom** (vertical seam)
  - **left → right** (horizontal seam)

At each iteration:

1. Compute an **energy map**
2. Find the **minimum-energy seam**
3. Remove the seam
4. Repeat `k` times

This keeps the most important regions (**high-energy areas**) untouched.

---

## ⚡ Energy Map

Energy represents pixel importance (edges/details).

In this project, energy is computed with Sobel gradients:

- **Energy = |Sobel_x| + |Sobel_y|**

✅ High energy ⇒ important pixels  
✅ Low energy ⇒ pixels that can be removed safely

---

## 🧠 Dynamic Programming (Minimum Seam)

To find the best seam efficiently, we use **Dynamic Programming**:

- Build a cumulative energy matrix `M`
- For each pixel, choose the minimum of the **3 pixels above** (left / up / right)
- Backtrack from the bottom row to recover the seam path

Complexity (per seam):

- Time: **O(H × W)**
- Space: **O(H × W)**

---

## ✨ App Features

✅ Upload an image (JPG/PNG)  
✅ Choose direction:

- Vertical seam removal
- Horizontal seam removal

✅ Select **k seams** to remove  
✅ Press **Play** to watch seam carving step-by-step  
✅ Seam overlay + energy visualization  
✅ Download the final resized image as PNG  

---

## ▶️ How to Run the App (Local)

### ✅ 1) Clone the repo

```bash
git clone https://github.com/SoumayaRomdhani/seam-carving-live-animation.git
cd seam-carving-live-animation

pip install -r requirements.txt

streamlit run app.py
