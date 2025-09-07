import pyray
import math
from pyray import Vector2, Vector3, Camera3D, CAMERA_PERSPECTIVE, KeyboardKey
from cube import Cube
from solver import KociembaSolver

class RubiksCube3D:
    def __init__(self, cube_instance):
        self.cube = cube_instance
        self.solver = KociembaSolver()
        self.solution = []
        self.solve_index = 0
        self.is_solving_all = False
        self.move_timer = 0
        self.MOVE_DELAY = 30 
        self.is_coloring_mode = False
        self.selected_face = None
        self.selected_row = -1
        self.selected_col = -1
        self.color_picker_pos = Vector2(0, 0)
        self.camera_is_movable = True

        self.screen_width = 800
        self.screen_height = 800
        pyray.init_window(self.screen_width, self.screen_height, "3D Rubik's Cube Solver")
        pyray.set_target_fps(60)

        self.camera = Camera3D()
        self.camera.position = Vector3(10.0, 10.0, 10.0)
        self.camera.target = Vector3(0.0, 0.0, 0.0)
        self.camera.up = Vector3(0.0, 1.0, 0.0)
        self.camera.fovy = 45.0
        self.camera.projection = CAMERA_PERSPECTIVE
        self.camera_speed = 0.5
        self.rotation_speed = 0.05
        self.angle_around_center = math.atan2(self.camera.position.x, self.camera.position.z)
        self.height = self.camera.position.y

        self.colors = {
            'W': pyray.WHITE, 'Y': pyray.YELLOW, 'G': pyray.GREEN,
            'B': pyray.BLUE, 'O': pyray.ORANGE, 'R': pyray.RED,
            'NONE': pyray.BLACK
        }
        self.color_picker_chars = ['W', 'Y', 'G', 'B', 'O', 'R']
        
        # Animation state
        self.is_animating_move = False
        self.current_move_notation = ""
        self.animation_progress = 0.0
        self.ANIMATION_FRAMES = 15
        self.active_color = None
        self.pause_timer = 0

        # Additional animation details stored when a move begins:
        self.anim_layer_indices = []
        self.anim_axis = Vector3(0,0,0)
        self.anim_total_angle = 0.0
        self.anim_color_map = {}
        
        self.cubelet_grid_positions = self._initialize_cubelet_grid_positions()
        
        # 2D map variables
        self.sticker_size = 50
        self.map_offset_x = 60
        self.map_offset_y = 145
        self.map_layout = {
            'U': (1, 0), 'L': (0, 1), 'F': (1, 1), 'R': (2, 1), 'B': (3, 1), 'D': (1, 2)
        }

    def _initialize_cubelet_grid_positions(self):
        grid_positions = []
        for x in range(3):
            for y in range(3):
                for z in range(3):
                    grid_positions.append(Vector3(x - 1, y - 1, z - 1))
        return grid_positions

    def _generate_facelet_positions_map(self):
        facelet_colors_map = {}
        cubelet_index = 0
        for x_grid in range(3):
            for y_grid in range(3):
                for z_grid in range(3):
                    colors = {}
                    # U: row = z, col = x
                    if y_grid == 2: colors['U'] = self.cube.faces['U'][z_grid][x_grid]
                    else: colors['U'] = 'NONE'
                    # ** FIX **: The D-face mapping was inverted along the z-axis.
                    # From below, the front row (row=0) corresponds to the front cubelets (z=2).
                    # D: row = 2 - z, col = x
                    if y_grid == 0: colors['D'] = self.cube.faces['D'][2 - z_grid][x_grid]
                    else: colors['D'] = 'NONE'
                    # F: row = 2 - y, col = x
                    if z_grid == 2: colors['F'] = self.cube.faces['F'][2 - y_grid][x_grid]
                    else: colors['F'] = 'NONE'
                    # B: row = 2 - y, col = 2 - x
                    if z_grid == 0: colors['B'] = self.cube.faces['B'][2 - y_grid][2 - x_grid]
                    else: colors['B'] = 'NONE'
                    # L: row = 2 - y, col = z
                    if x_grid == 0: colors['L'] = self.cube.faces['L'][2 - y_grid][z_grid]
                    else: colors['L'] = 'NONE'
                    # R: row = 2 - y, col = 2 - z
                    if x_grid == 2: colors['R'] = self.cube.faces['R'][2 - y_grid][2 - z_grid]
                    else: colors['R'] = 'NONE'

                    facelet_colors_map[cubelet_index] = colors
                    cubelet_index += 1
        return facelet_colors_map

    
    def update(self):
        self.handle_input()
        
        if self.is_solving_all:
            if self.is_animating_move:
                self.animation_progress += 1
                if self.animation_progress >= self.ANIMATION_FRAMES:
                    # Apply logical move and stop animation
                    self.cube.execute_move(self.current_move_notation)
                    self.is_animating_move = False
                    self.animation_progress = 0.0
                    self.anim_layer_indices = []
                    self.anim_axis = Vector3(0,0,0)
                    self.anim_total_angle = 0.0
                    self.pause_timer = 30 
            elif self.pause_timer > 0:
                self.pause_timer -= 1
            else:
                if self.solve_index < len(self.solution):
                    self.start_animation_for_move(self.solution[self.solve_index])
                    self.solve_index += 1
                else:
                    self.is_solving_all = False
                    self.current_move_notation = ""
                    print("All moves executed. Cube is solved.")
        
        if self.is_animating_move and not self.is_solving_all:
            self.animation_progress += 1
            if self.animation_progress >= self.ANIMATION_FRAMES:
                self.cube.execute_move(self.current_move_notation)
                self.is_animating_move = False
                self.animation_progress = 0.0
                self.anim_layer_indices = []
                self.anim_axis = Vector3(0,0,0)
                self.anim_total_angle = 0.0

    def start_animation_for_move(self, notation):
        if self.is_animating_move: return
        
        self.current_move_notation = notation
        self.animation_progress = 0.0

        face_char = notation[0]
        is_double_turn = notation.endswith('2')
        is_counter_clockwise = notation.endswith("'")

        total_angle = 90.0
        if is_double_turn: total_angle = 180.0

        if face_char == 'U': axis = Vector3(0, 1, 0)
        elif face_char == 'D': axis = Vector3(0, -1, 0)
        elif face_char == 'F': axis = Vector3(0, 0, 1)
        elif face_char == 'B': axis = Vector3(0, 0, -1)
        elif face_char == 'L': axis = Vector3(-1, 0, 0)
        elif face_char == 'R': axis = Vector3(1, 0, 0)
        else: return

        if is_counter_clockwise: total_angle *= -1.0
        
        total_angle *= -1.0  

        self.anim_axis = axis
        self.anim_total_angle = total_angle
        self.anim_layer_indices = self._get_cubelets_in_layer(face_char)
        
        self.anim_color_map = self._generate_facelet_positions_map()
        
        self.is_animating_move = True

        print(f"Starting animation for move: {notation}. "
            f"Layer cubelets: {self.anim_layer_indices}, "
            f"axis: {self.anim_axis}, angle: {self.anim_total_angle}")

    def _get_cubelets_in_layer(self, face_char):
        layer_indices = []
        cubelet_index = 0
        for x_grid in range(3):
            for y_grid in range(3):
                for z_grid in range(3):
                    if face_char == 'U' and y_grid == 2: layer_indices.append(cubelet_index)
                    elif face_char == 'D' and y_grid == 0: layer_indices.append(cubelet_index)
                    elif face_char == 'F' and z_grid == 2: layer_indices.append(cubelet_index)
                    elif face_char == 'B' and z_grid == 0: layer_indices.append(cubelet_index)
                    elif face_char == 'L' and x_grid == 0: layer_indices.append(cubelet_index)
                    elif face_char == 'R' and x_grid == 2: layer_indices.append(cubelet_index)
                    cubelet_index += 1
        return layer_indices

    def draw_cube(self):
        if self.is_animating_move:
            facelet_colors_map = self.anim_color_map
        else:
            facelet_colors_map = self._generate_facelet_positions_map()
        
        current_angle_degrees = 0.0
        if self.is_animating_move:
            prog = max(0.0, min(self.animation_progress, self.ANIMATION_FRAMES))
            fraction = prog / float(self.ANIMATION_FRAMES)
            current_angle_degrees = fraction * self.anim_total_angle

        cubelet_index = 0
        for x_grid in range(3):
            for y_grid in range(3):
                for z_grid in range(3):
                    base_pos = self.cubelet_grid_positions[cubelet_index]
                    pyray.rl_push_matrix()

                    if self.is_animating_move and cubelet_index in self.anim_layer_indices:
                        pyray.rl_rotatef(current_angle_degrees, self.anim_axis.x, self.anim_axis.y, self.anim_axis.z)
                        pyray.rl_translatef(base_pos.x, base_pos.y, base_pos.z)
                    else:
                        pyray.rl_translatef(base_pos.x, base_pos.y, base_pos.z)

                    pyray.draw_cube(Vector3(0,0,0), 0.95, 0.95, 0.95, self.colors['NONE'])
                    
                    colors_for_this_cubelet = facelet_colors_map[cubelet_index]
                    
                    if colors_for_this_cubelet['U'] != 'NONE':
                        pyray.draw_cube(Vector3(0, 0.475, 0), 0.9, 0.05, 0.9, self.colors[colors_for_this_cubelet['U']])
                    if colors_for_this_cubelet['D'] != 'NONE':
                        pyray.draw_cube(Vector3(0, -0.475, 0), 0.9, 0.05, 0.9, self.colors[colors_for_this_cubelet['D']])
                    if colors_for_this_cubelet['F'] != 'NONE':
                        pyray.draw_cube(Vector3(0, 0, 0.475), 0.9, 0.9, 0.05, self.colors[colors_for_this_cubelet['F']])
                    if colors_for_this_cubelet['B'] != 'NONE':
                        pyray.draw_cube(Vector3(0, 0, -0.475), 0.9, 0.9, 0.05, self.colors[colors_for_this_cubelet['B']])
                    if colors_for_this_cubelet['L'] != 'NONE':
                        pyray.draw_cube(Vector3(-0.475, 0, 0), 0.05, 0.9, 0.9, self.colors[colors_for_this_cubelet['L']])
                    if colors_for_this_cubelet['R'] != 'NONE':
                        pyray.draw_cube(Vector3(0.475, 0, 0), 0.05, 0.9, 0.9, self.colors[colors_for_this_cubelet['R']])
                    pyray.rl_pop_matrix()
                    cubelet_index += 1

    def handle_input(self):
        if self.is_coloring_mode:
            self._handle_coloring_input()
        else:
            self._handle_normal_input()

    def _handle_normal_input(self):
        if self.camera_is_movable:
            if pyray.is_key_down(KeyboardKey.KEY_RIGHT): self.angle_around_center -= self.rotation_speed
            if pyray.is_key_down(KeyboardKey.KEY_LEFT): self.angle_around_center += self.rotation_speed
            if pyray.is_key_down(KeyboardKey.KEY_UP): self.height += self.camera_speed
            if pyray.is_key_down(KeyboardKey.KEY_DOWN): self.height -= self.camera_speed
            
            radius = math.sqrt(self.camera.position.x**2 + self.camera.position.z**2)
            self.camera.position.x = radius * math.sin(self.angle_around_center)
            self.camera.position.y = self.height
            self.camera.position.z = radius * math.cos(self.angle_around_center)
        
        if not self.is_animating_move:
            if pyray.is_key_pressed(KeyboardKey.KEY_S): self.scramble()
            if pyray.is_key_pressed(KeyboardKey.KEY_R): self.reset_cube()
            if pyray.is_key_pressed(KeyboardKey.KEY_P): self.start_solve()
            if pyray.is_key_pressed(KeyboardKey.KEY_N): 
                if self.solution and self.solve_index < len(self.solution):
                    self.start_animation_for_move(self.solution[self.solve_index])
                    self.solve_index += 1
            if pyray.is_key_pressed(KeyboardKey.KEY_A): self.solve_all_moves()
            if pyray.is_key_pressed(KeyboardKey.KEY_I):
                self.is_coloring_mode = True
                self.is_solving_all = False
                self.solution = []
                self.selected_face = None
                self.selected_row = -1
                self.selected_col = -1
                self.camera_is_movable = False
                self.active_color = None

    def _handle_coloring_input(self):
        if pyray.is_key_pressed(KeyboardKey.KEY_ENTER):
            self.is_coloring_mode = False
            self.selected_face = None
            self.camera_is_movable = True
            self.active_color = None
            print("Coloring mode exited. Press 'P' to solve your cube.")
            return

        if pyray.is_mouse_button_pressed(pyray.MouseButton.MOUSE_BUTTON_LEFT):
            mouse_pos = pyray.get_mouse_position()
            
            picker_box_width = 40; picker_box_height = 40; picker_margin = 10
            picker_start_x = self.screen_width // 2 - (len(self.color_picker_chars) * (picker_box_width + picker_margin)) // 2
            picker_start_y = self.screen_height - 100
            
            for i, color_char in enumerate(self.color_picker_chars):
                picker_rect = pyray.Rectangle(picker_start_x + i * (picker_box_width + picker_margin), picker_start_y, picker_box_width, picker_box_height)
                if pyray.check_collision_point_rec(mouse_pos, picker_rect):
                    self.active_color = color_char
                    print(f"Active color set to: {self.active_color}")
                    return

            for face_name, (grid_x, grid_y) in self.map_layout.items():
                face_x = self.map_offset_x + grid_x * (self.sticker_size * 3 + 20)
                face_y = self.map_offset_y + grid_y * (self.sticker_size * 3 + 20)
                
                for r in range(3):
                    for c in range(3):
                        sticker_rect = pyray.Rectangle(face_x + c * self.sticker_size, face_y + r * self.sticker_size, self.sticker_size, self.sticker_size)
                        
                        if pyray.check_collision_point_rec(mouse_pos, sticker_rect):
                            if self.active_color is not None:
                                self.cube.faces[face_name][r][c] = self.active_color
                                print(f"Sticker {face_name}[{r}][{c}] set to {self.active_color}")
                            self.selected_face = face_name
                            self.selected_row = r
                            self.selected_col = c
                            return

    def scramble(self):
        self.solution = []; self.solve_index = 0; self.is_solving_all = False
        self.current_move_notation = ""
        print("Scrambling...")
        scramble_seq = self.cube.scramble(20)
        print(f"Scrambled: {' '.join(scramble_seq)}. Press 'P' to solve.")
        
    def reset_cube(self):
        self.cube.reset(); self.solution = []; self.solve_index = 0; self.is_solving_all = False
        self.current_move_notation = ""
        print("Cube reset to solved state. Press 'S' to scramble.")

    def start_solve(self):
        print("Solving...")
        try:
            self.solution = self.solver.solve(self.cube)
            self.solve_index = 0
            self.current_move_notation = ""
            if self.solution: print(f"Solution found! {len(self.solution)} moves. Press 'N' for next move or 'A' for animated solve.")
            else: print("Cube is already solved or an error occurred.")
        except RuntimeError as e: print(f"Solver Error: {e}")

    def solve_all_moves(self):
        if not self.solution:
            print("No solution available. Press 'P' to solve first.")
            return
        if self.is_solving_all: return
        self.is_solving_all = True
        print("Starting animated solve...")

    def run(self):
        while not pyray.window_should_close():
            self.update()
            pyray.begin_drawing()
            pyray.clear_background(pyray.RAYWHITE)
            
            if self.is_coloring_mode:
                self._draw_coloring_ui()
            else:
                pyray.begin_mode_3d(self.camera)
                self.draw_cube()
                pyray.draw_grid(10, 1.0)
                pyray.end_mode_3d()
                pyray.draw_text("R: Reset, S: Scramble, P: Solve, N: Next Move, A: Solve All", 10, 10, 12, pyray.BLACK)
                pyray.draw_text("I: Enter/Exit Custom Scramble Mode", 10, 30, 12, pyray.BLACK)
                if self.current_move_notation:
                    pyray.draw_text(f"Executing move: {self.current_move_notation}", 10, 70, 15, pyray.DARKGRAY)
                if self.camera_is_movable:
                    pyray.draw_text("Arrow keys to rotate and move camera", 10, 50, 12, pyray.BLACK)

            pyray.end_drawing()
        pyray.close_window()
    
    def _draw_coloring_ui(self):
        pyray.draw_rectangle(0, 0, self.screen_width, self.screen_height, pyray.fade(pyray.BLACK, 0.7))
        pyray.draw_text("INTERACTIVE COLORING MODE", int(self.screen_width / 2 - pyray.measure_text("INTERACTIVE COLORING MODE", 20) / 2), 20, 20, pyray.RAYWHITE)
        pyray.draw_text("Click a color below to select it.", int(self.screen_width / 2 - pyray.measure_text("Click a color below to select it.", 15) / 2), 50, 15, pyray.RAYWHITE)
        pyray.draw_text("Then click a sticker on the grid to apply.", int(self.screen_width / 2 - pyray.measure_text("Then click a sticker on the grid to apply.", 15) / 2), 70, 15, pyray.RAYWHITE)
        pyray.draw_text("Press ENTER to finish.", int(self.screen_width / 2 - pyray.measure_text("Press ENTER to finish.", 15) / 2), 90, 15, pyray.RAYWHITE)
        
        for face_name, (grid_x, grid_y) in self.map_layout.items():
            face_x = self.map_offset_x + grid_x * (self.sticker_size * 3 + 20)
            face_y = self.map_offset_y + grid_y * (self.sticker_size * 3 + 20)

            pyray.draw_text(face_name, int(face_x + self.sticker_size * 1.5 - 5), int(face_y - 20), 15, pyray.RAYWHITE)

            for r in range(3):
                for c in range(3):
                    sticker_x = face_x + c * self.sticker_size
                    sticker_y = face_y + r * self.sticker_size
                    
                    color_char = self.cube.faces[face_name][r][c]
                    color_pyray = self.colors[color_char]
                    
                    pyray.draw_rectangle(sticker_x, sticker_y, self.sticker_size, self.sticker_size, color_pyray)
                    
                    if self.selected_face == face_name and self.selected_row == r and self.selected_col == c:
                        pyray.draw_rectangle_lines_ex(pyray.Rectangle(sticker_x, sticker_y, self.sticker_size, self.sticker_size), 3, pyray.GOLD)
                    else:
                        pyray.draw_rectangle_lines(sticker_x, sticker_y, self.sticker_size, self.sticker_size, pyray.BLACK)

        picker_box_width = 40; picker_box_height = 40; picker_margin = 10
        picker_start_x = self.screen_width // 2 - (len(self.color_picker_chars) * (picker_box_width + picker_margin)) // 2
        picker_start_y = self.screen_height - 100
        
        for i, color_char in enumerate(self.color_picker_chars):
            color_pyray = self.colors[color_char]
            picker_rect = pyray.Rectangle(picker_start_x + i * (picker_box_width + picker_margin), picker_start_y, picker_box_width, picker_box_height)
            pyray.draw_rectangle_rec(picker_rect, color_pyray)
            
            if self.active_color == color_char:
                pyray.draw_rectangle_lines_ex(picker_rect, 5, pyray.GOLD)
            else:
                pyray.draw_rectangle_lines_ex(picker_rect, 2, pyray.RAYWHITE)
