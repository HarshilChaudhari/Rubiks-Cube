# 🟥🟧🟨🟩🟦🟪 3D Rubik's Cube Solver 🟥🟧🟨🟩🟦🟪

A **Python** application to interact with, scramble, and solve a **3D Rubik's Cube** using **PyRay**. Includes animated solving, interactive coloring mode, and real-time 3D manipulation.

---

## 🎯 Features

- **🟦 3D Interactive Rubik's Cube**
  - Rotate and move the camera around the cube.
  - Zoom in/out with arrow keys.

- **🟥 Scramble & Solve**
  - Random scramble sequences.
  - Solve with **Kociemba algorithm**.
  - Step-by-step or full animated solve.

- **🟨 Custom Coloring Mode**
  - Click stickers to set colors.
  - Supports all 6 cube colors: 🟦 Blue, 🟩 Green, 🟨 Yellow, 🟥 Red, 🟧 Orange, ⬜ White.

- **🟩 Smooth Animation**
  - Rotating cube layers during solving.
  - Adjustable animation speed.

- **🟧 2D Face Map**
  - Shows a 2D representation for easier coloring.

---

## 🛠 Installation

1. Clone the repository:

```bash
git clone https://github.com/HarshilChaudhari/Rubiks-Cube.git
cd Rubiks-Cube
````

2. Create a virtual environment and activate:

```bash
python -m venv my_venv
source my_venv/bin/activate      # Linux/macOS
my_venv\Scripts\activate         # Windows
```

3. Install dependencies:

```bash
pip install raylib
```

> Python 3.10+ recommended.

---

## 📂 File Structure

```
Rubiks-Cube/
│
├── main.py            # Entry point
├── renderer.py        # 3D cube rendering and input
├── cube.py            # Cube operations
├── solver.py          # Kociemba solver
└── README.md          # Project documentation
```

---

## 🚀 Usage

Run the application:

```bash
python main.py
```

---

## 🚀 Running the Packaged Executable

If you have built or downloaded the packaged version from the **`dist/`** folder (using PyInstaller), you can run the application directly without setting up Python or installing dependencies.

### 🖥️ Windows

```powershell
dist\main.exe
```

### 🍎 macOS / 🐧 Linux

```bash
./dist/main
```

> 💡 On **macOS**, if Gatekeeper blocks the app, allow it from
> **System Preferences → Security & Privacy → Open Anyway**.
>
> 💡 On **Linux**, ensure the file is executable:
>
> ```bash
> chmod +x dist/main
> ./dist/main
> ```

---

### 🎮 Controls

* **Camera Movement:**
  `Arrow Keys` → Rotate and move the camera.

* **Cube Manipulation:**
  `R` → Reset cube
  `S` → Scramble cube
  `P` → Solve cube
  `N` → Next move
  `A` → Solve all moves (animated)

* **Interactive Coloring Mode:**
  `I` → Enter coloring mode
  Click a color → Click sticker → Apply
  `Enter` → Exit coloring mode

---

## 📦 Dependencies

* [Python raylib](https://pypi.org/project/raylib/) — 3D graphics for Python (Python Bindings for Raylib 5.5)
* Python 3.10+

---

## ⚠️ Notes

* Uses **Kociemba’s algorithm** internally; ensure cube states are valid.
* Adjust animation speed via `ANIMATION_FRAMES` and `MOVE_DELAY` in `renderer.py`.
* Compatible with macOS, Linux, and Windows.

---

## 🎨 Cube Colors Legend

| Color  | Emoji |
| ------ | ----- |
| White  | ⬜     |
| Yellow | 🟨    |
| Green  | 🟩    |
| Blue   | 🟦    |
| Orange | 🟧    |
| Red    | 🟥    |
