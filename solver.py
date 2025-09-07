from collections import Counter
import kociemba


class KociembaSolver:
    def __init__(self):
        pass

    def _build_facelet_string(self, cube):
        centers = {f: cube.faces[f][1][1] for f in cube.faces}
        color_to_face = {color: face for face, color in centers.items()}

        order = ['U', 'R', 'F', 'D', 'L', 'B']
        facelets = []
        for face in order:
            for r in range(3):
                for c in range(3):
                    sticker = cube.faces[face][r][c]
                    if sticker not in color_to_face:
                        raise ValueError(f"Sticker color '{sticker}' not found among centers {centers}")
                    facelets.append(color_to_face[sticker])

        return ''.join(facelets)

    def _validate_facelet_string(self, facelets):
        if len(facelets) != 54:
            raise ValueError(f"Facelet string wrong length: {len(facelets)} (expected 54).")
        cnt = Counter(facelets)
        required = {ch: 9 for ch in "URFDLB"}
        if any(cnt[ch] != required[ch] for ch in required):
            raise ValueError(f"Facelet counts incorrect: {cnt}")
        return True

    def solve(self, cube):
        try:
            facelets = self._build_facelet_string(cube)
            self._validate_facelet_string(facelets)
            solution_str = kociemba.solve(facelets)
            return solution_str.strip().split()
        except Exception as e:
            raise RuntimeError(f"Solver failed: {e}")
