import random
from copy import deepcopy
import pyray


class Cube:
    def __init__(self):
        self._initial_state = {
            'U': [['W'] * 3 for _ in range(3)], 'D': [['Y'] * 3 for _ in range(3)],
            'F': [['G'] * 3 for _ in range(3)], 'B': [['B'] * 3 for _ in range(3)],
            'L': [['O'] * 3 for _ in range(3)], 'R': [['R'] * 3 for _ in range(3)]
        }
        self.faces = deepcopy(self._initial_state)
        self._gui_color_map = {
            'W': pyray.WHITE, 'Y': pyray.YELLOW, 'G': pyray.GREEN,
            'B': pyray.BLUE, 'O': pyray.ORANGE, 'R': pyray.RED
        }
        self._faces_order = ['U', 'R', 'F', 'D', 'L', 'B']
        self._face_offset = {f: i * 9 for i, f in enumerate(self._faces_order)}
        self._face_rc_to_index = {}
        self._index_to_face_rc = {}

        for face in self._faces_order:
            base = self._face_offset[face]
            for r in range(3):
                for c in range(3):
                    idx = base + r * 3 + c
                    self._face_rc_to_index[(face, r, c)] = idx
                    self._index_to_face_rc[idx] = (face, r, c)

        self._perm_cw = {f: self._build_perm_for_face(f) for f in self._faces_order}

    def get_state(self):
        return deepcopy(self.faces)

    def set_state(self, state):
        self.faces = deepcopy(state)

    def reset(self):
        self.faces = deepcopy(self._initial_state)

    def is_solved(self):
        for f in self.faces:
            color = self.faces[f][1][1]
            for row in self.faces[f]:
                for s in row:
                    if s != color:
                        return False
        return True

    def to_string(self):
        s = []
        for f in self._faces_order:
            for row in self.faces[f]:
                s.extend(row)
        return ''.join(s)

    def execute_move(self, notation):
        if len(notation) == 0:
            return
        face = notation[0]
        if face not in self._perm_cw:
            raise ValueError(f"Unknown face in move: {notation}")

        if notation.endswith("2"):
            self._apply_perm(self._perm_cw[face])
            self._apply_perm(self._perm_cw[face])
        elif notation.endswith("'"):
            for _ in range(3):
                self._apply_perm(self._perm_cw[face])
        else:
            self._apply_perm(self._perm_cw[face])

    def scramble(self, length=20):
        all_moves = [
            'F', "F'", 'F2', 'B', "B'", 'B2',
            'U', "U'", 'U2', 'D', "D'", 'D2',
            'L', "L'", 'L2', 'R', "R'", 'R2'
        ]
        seq = [random.choice(all_moves) for _ in range(length)]
        for m in seq:
            self.execute_move(m)
        return seq

    def _build_perm_for_face(self, face):
        perm = list(range(54))
        base = self._face_offset[face]
        local_map = {0: 6, 1: 3, 2: 0, 3: 7, 4: 4, 5: 1, 6: 8, 7: 5, 8: 2}

        for new_local, old_local in local_map.items():
            perm[base + new_local] = base + old_local

        adj = {
            'U': [(45, 46, 47), (9, 10, 11), (18, 19, 20), (36, 37, 38)],
            'D': [(24, 25, 26), (15, 16, 17), (51, 52, 53), (42, 43, 44)],
            'F': [(6, 7, 8), (9, 12, 15), (29, 28, 27), (44, 41, 38)],
            'B': [(2, 1, 0), (36, 39, 42), (33, 34, 35), (17, 14, 11)],
            'L': [(0, 3, 6), (18, 21, 24), (27, 30, 33), (53, 50, 47)],
            'R': [(8, 5, 2), (45, 48, 51), (35, 32, 29), (26, 23, 20)]
        }

        strips = adj[face]
        for i in range(4):
            new_strip, old_strip = strips[i], strips[(i - 1) % 4]
            for j in range(3):
                perm[new_strip[j]] = old_strip[j]

        return perm

    def _apply_perm(self, perm):
        flat = [
            self.faces[self._index_to_face_rc[i][0]][self._index_to_face_rc[i][1]][self._index_to_face_rc[i][2]]
            for i in range(54)
        ]
        new_flat = [flat[perm[i]] for i in range(54)]

        for i in range(54):
            face, r, c = self._index_to_face_rc[i]
            self.faces[face][r][c] = new_flat[i]
