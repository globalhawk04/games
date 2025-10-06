import arcade

# --- Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
SCREEN_TITLE = "Rectangle Drawing Test"

class RectangleDrawingGame(arcade.Window):
    """ Simple game to test drawing rectangles. """

    def __init__(self, width, height, title):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(width, height, title)

        # Set the background color (optional - clear will use this)
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        """ Set up the game here. This is called once when the game starts. """
        pass

    def on_draw(self):
        """ Render the screen. """

        # This command should clear the screen before we start drawing
        # In an arcade.Window subclass, use self.clear() instead of arcade.start_render()
        self.clear()

        # --- Drawing Rectangles ---

        # Draw a filled red rectangle in the center-ish
        try:
            arcade.draw_rectangle_filled(
                center_x=SCREEN_WIDTH / 2,
                center_y=SCREEN_HEIGHT / 2,
                width=100,
                height=150,
                color=arcade.color.RED
            )
            print("Successfully called arcade.draw_rectangle_filled (RED)")
        except AttributeError as e:
            print(f"AttributeError when calling draw_rectangle_filled (RED): {e}")


        # Draw another filled blue rectangle
        try:
            arcade.draw_rectangle_filled(
                center_x=150,
                center_y=100,
                width=80,
                height=50,
                color=arcade.color.BLUE
            )
            print("Successfully called arcade.draw_rectangle_filled (BLUE)")
        except AttributeError as e:
             print(f"AttributeError when calling draw_rectangle_filled (BLUE): {e}")


        # Draw an outlined green rectangle
        try:
            arcade.draw_rectangle_outline(
                center_x=SCREEN_WIDTH - 150,
                center_y=SCREEN_HEIGHT - 100,
                width=120,
                height=70,
                color=arcade.color.GREEN,
                border_width=5 # Thickness of the outline
            )
            print("Successfully called arcade.draw_rectangle_outline (GREEN)")
        except AttributeError as e:
             print(f"AttributeError when calling draw_rectangle_outline (GREEN): {e}")

        # Draw another outlined yellow rectangle
        try:
            arcade.draw_rectangle_outline(
                center_x=450,
                center_y=300,
                width=60,
                height=100,
                color=arcade.color.YELLOW,
                border_width=3
            )
            print("Successfully called arcade.draw_rectangle_outline (YELLOW)")
        except AttributeError as e:
             print(f"AttributeError when calling draw_rectangle_outline (YELLOW): {e}")

        # arcade.finish_render() # You also don't call finish_render() in on_draw


    def on_update(self, delta_time):
        """ Movement and game logic. (Not used in this example)"""
        pass

    def on_key_press(self, key, modifiers):
        """ Called whenever a key is pressed. (Not used in this example)"""
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        """ Called when the mouse moves. (Not used in this example)"""
        pass


def main():
    """ Main function to start the game. """
    game = RectangleDrawingGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    game.setup()
    arcade.run()

# Run the main function when the script is executed
if __name__ == "__main__":
    main()