from cube import Cube
from renderer import RubiksCube3D


if __name__ == "__main__":
    my_cube = Cube()
    app = RubiksCube3D(my_cube)
    app.run()
