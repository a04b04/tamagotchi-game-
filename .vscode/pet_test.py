import jpegdec

from time import sleep, ticks_ms, ticks_diff
from pet import Pet

from picographics import PicoGraphics, DISPLAY_TUFTY_2040
from pimoroni import Button


display = PicoGraphics(display=DISPLAY_TUFTY_2040)
display.set_backlight(1.0)

jpeg = jpegdec.JPEG(display)

button_left = Button(7, invert=False)      # A
button_select = Button(8, invert=False)    # B
button_right = Button(9, invert=False)     # C
button_up = Button(22, invert=False)
button_down = Button(6, invert=False)

WIDTH, HEIGHT = display.get_bounds()

WHITE = display.create_pen(255, 255, 255)
BLACK = display.create_pen(0, 0, 0)
BLUE = display.create_pen(0, 120, 255)
LIGHT_GREY = display.create_pen(220, 220, 220)
PET_COLOUR = display.create_pen(73, 216, 230)

WALL = display.create_pen(220, 240, 255)
FLOOR = display.create_pen(205, 170, 120)
SKIRTING = display.create_pen(150, 110, 70)
WINDOW_BLUE = display.create_pen(170, 220, 255)
WINDOW_FRAME = display.create_pen(90, 120, 150)
PLANT_GREEN = display.create_pen(80, 170, 90)
PLANT_POT = display.create_pen(180, 110, 70)

cursor_x = 145
cursor_y = 100
cursor_size = 12
move_speed = 6

box_y = 180
box_width = 52
box_height = 50
box_gap = 10
first_box_x = 10

byte = Pet()

last_stat_decrease = ticks_ms()
stat_decrease_interval = 5000

message = ""
message_timer = 0
button_was_pressed = False


def draw_action_boxes():
    for index in range(5):
        x = first_box_x + index * (box_width + box_gap)

        display.set_pen(LIGHT_GREY)
        display.rectangle(x, box_y, box_width, box_height)

        display.set_pen(BLACK)
        display.line(x, box_y, x + box_width, box_y)
        display.line(x, box_y, x, box_y + box_height)
        display.line(x + box_width, box_y, x + box_width, box_y + box_height)
        display.line(x, box_y + box_height, x + box_width, box_y + box_height)


def draw_food_icon(x, y):
    display.set_pen(BLACK)

    # Handle
    display.rectangle(x + 23, y + 23, 6, 18)

    # Fork head
    display.rectangle(x + 17, y + 12, 18, 12)

    # Gaps between prongs
    display.set_pen(LIGHT_GREY)
    display.rectangle(x + 20, y + 10, 3, 11)
    display.rectangle(x + 25, y + 10, 3, 11)
    display.rectangle(x + 30, y + 10, 3, 11)


def draw_play_icon(x, y):
    display.set_pen(BLACK)

    # Left end
    display.circle(x + 15, y + 21, 5)
    display.circle(x + 15, y + 29, 5)

    # Right end
    display.circle(x + 37, y + 21, 5)
    display.circle(x + 37, y + 29, 5)

    # Middle shaft
    display.rectangle(x + 15, y + 21, 22, 8)


def draw_clean_icon(x, y):
    display.set_pen(BLACK)

    # Shower head
    display.rectangle(x + 14, y + 15, 24, 7)

    # Curved-ish top using lines
    display.line(x + 17, y + 15, x + 20, y + 10)
    display.line(x + 20, y + 10, x + 32, y + 10)
    display.line(x + 32, y + 10, x + 35, y + 15)

    # Water drops
    display.line(x + 18, y + 27, x + 16, y + 33)
    display.line(x + 16, y + 33, x + 18, y + 36)
    display.line(x + 18, y + 36, x + 20, y + 33)

    display.line(x + 26, y + 25, x + 24, y + 31)
    display.line(x + 24, y + 31, x + 26, y + 34)
    display.line(x + 26, y + 34, x + 28, y + 31)

    display.line(x + 34, y + 27, x + 32, y + 33)
    display.line(x + 32, y + 33, x + 34, y + 36)
    display.line(x + 34, y + 36, x + 36, y + 33)


def draw_sleep_icon(x, y):
    # Crescent moon
    display.set_pen(BLACK)
    display.circle(x + 27, y + 25, 15)

    display.set_pen(LIGHT_GREY)
    display.circle(x + 34, y + 19, 13)


def draw_stats_icon(x, y):
    # Bar chart
    display.set_pen(BLACK)
    display.rectangle(x + 11, y + 29, 7, 10)
    display.rectangle(x + 23, y + 20, 7, 19)
    display.rectangle(x + 35, y + 12, 7, 27)

    display.line(x + 8, y + 40, x + 45, y + 40)


def get_selected_action():
    for index in range(5):
        box_x = first_box_x + index * (box_width + box_gap)

        cursor_is_inside = (
            cursor_x + cursor_size > box_x
            and cursor_x < box_x + box_width
            and cursor_y + cursor_size > box_y
            and cursor_y < box_y + box_height
        )

        if cursor_is_inside:
            return index

    return None


def get_pet_state():
    if(
        byte.hunger >= 80
        and byte.energy >= 80
        and byte.cleanliness >= 80
        and byte.happiness >= 80
    ):
        return "perfect"
    if byte.hunger < 30:
        return "hungry"
    if byte.energy < 30:
        return "tired"
    if byte.cleanliness < 30:
        return "dirty"
    if byte.happiness < 30 :
        return "play"
    return "normal"


def draw_pet_face(state):
    centre_x = 160
    centre_y = 105

    display.set_pen(PET_COLOUR)
    display.circle(centre_x, centre_y, 45)

    display.set_pen(BLACK)

    if state == "perfect":
        display.line(
            centre_x - 22,
            centre_y - 10,
            centre_x - 15,
            centre_y - 16
        )
        display.line(
            centre_x - 15,
            centre_y - 16,
            centre_x - 8,
            centre_y - 10
        )

        display.line(
            centre_x + 8,
            centre_y - 10,
            centre_x + 15,
            centre_y - 16
        )
        display.line(
            centre_x + 15,
            centre_y - 16,
            centre_x + 22,
            centre_y - 10
        )

        display.line(
            centre_x - 18,
            centre_y + 14,
            centre_x,
            centre_y + 25
        )
        display.line(
            centre_x,
            centre_y + 25,
            centre_x + 18,
            centre_y + 14
        )

    elif state == "play":
        display.circle(centre_x - 16, centre_y - 10, 4)
        display.circle(centre_x + 16, centre_y - 10, 4)
        display.rectangle(centre_x - 18, centre_y + 10, 36, 14)

    elif state == "hungry":
        display.circle(centre_x - 16, centre_y - 10, 4)
        display.circle(centre_x + 16, centre_y - 10, 4)
        display.circle(centre_x, centre_y + 18, 10)

    elif state == "tired":
        display.line(
            centre_x - 24,
            centre_y - 8,
            centre_x - 8,
            centre_y - 8
        )
        display.line(
            centre_x + 8,
            centre_y - 8,
            centre_x + 24,
            centre_y - 8
        )

        display.line(
            centre_x - 15,
            centre_y + 24,
            centre_x,
            centre_y + 15
        )
        display.line(
            centre_x,
            centre_y + 15,
            centre_x + 15,
            centre_y + 24
        )

        display.text(
            "Z",
            centre_x + 42,
            centre_y - 35,
            scale=2
        )

    elif state == "dirty":
        display.circle(centre_x - 16, centre_y - 10, 4)
        display.circle(centre_x + 16, centre_y - 10, 4)

        display.line(
            centre_x - 15,
            centre_y + 18,
            centre_x + 15,
            centre_y + 18
        )

        display.line(
            centre_x - 38,
            centre_y + 5,
            centre_x - 28,
            centre_y + 12
        )
        display.line(
            centre_x + 28,
            centre_y - 25,
            centre_x + 38,
            centre_y - 18
        )


def get_pet_message(state):
    if state == "hungry":
        return "I'm hungry!"

    if state == "tired":
        return "I'm tired..."

    if state == "dirty":
        return "Clean me!"

    if state == "play":
        return "Play with me!"

    return "I'm perfect!"

def show_pet_image(state):
    if state == "hungry":
        image_name = "image.jpeg"

    elif state == "tired":
        image_name = "dogtired.jpeg"

    elif state == "dirty":
        image_name = "dirtydog.jpeg"

    elif state == "perfect":
        image_name = "perfectdog.jpeg"

    else:
        image_name = "normaldog.jpeg"

    jpeg.open_file(image_name)

    # Coods depend on image size 
    jpeg.decode(100, 45)

def draw_background():
    # Wall
    display.set_pen(WALL)
    display.clear()

    # Window
    display.set_pen(WINDOW_FRAME)
    display.rectangle(20, 35, 65, 55)

    display.set_pen(WINDOW_BLUE)
    display.rectangle(24, 39, 57, 47)

    display.set_pen(WINDOW_FRAME)
    display.rectangle(50, 39, 4, 47)
    display.rectangle(24, 61, 57, 4)

    # Small plant
    display.set_pen(PLANT_POT)
    display.rectangle(268, 130, 24, 25)

    display.set_pen(PLANT_GREEN)
    display.circle(274, 128, 9)
    display.circle(286, 125, 10)
    display.circle(280, 116, 9)

    # Skirting board
    display.set_pen(SKIRTING)
    display.rectangle(0, 158, WIDTH, 6)

    # Floor
    display.set_pen(FLOOR)
    display.rectangle(0, 164, WIDTH, 16)

    # Simple floor lines
    display.set_pen(SKIRTING)
    display.line(0, 172, WIDTH, 172)

while True:
    # Cursor movement
    if button_left.is_pressed:
        cursor_x -= move_speed

    if button_right.is_pressed:
        cursor_x += move_speed

    if button_up.is_pressed:
        cursor_y -= move_speed

    if button_down.is_pressed:
        cursor_y += move_speed

    # Keep cursor on screen
    if cursor_x < 0:
        cursor_x = 0

    if cursor_x > WIDTH - cursor_size:
        cursor_x = WIDTH - cursor_size

    if cursor_y < 0:
        cursor_y = 0

    if cursor_y > HEIGHT - cursor_size:
        cursor_y = HEIGHT - cursor_size

    # Decrease one random stat every 5 seconds
    current_time = ticks_ms()

    if ticks_diff(
        current_time,
        last_stat_decrease
    ) >= stat_decrease_interval:
        byte.decrease_stats()
        last_stat_decrease = current_time

    # Handle B selection
    if button_select.is_pressed and not button_was_pressed:
        selected_action = get_selected_action()

        if selected_action == 0:
            byte.feed()
            message = "Yum!"

        elif selected_action == 1:
            byte.play()
            message = "Let's play!"

        elif selected_action == 2:
            byte.clean()
            message = "All clean!"

        elif selected_action == 3:
            byte.sleep()
            message = "Zzz..."

        elif selected_action == 4:
            message = "stats"

        else:
            message = "Move onto an icon"

        message_timer = 80
        button_was_pressed = True

    if not button_select.is_pressed:
        button_was_pressed = False

    pet_state = get_pet_state()

    # Draw background
    draw_background()

    display.set_pen(BLACK)
    display.text("BYTE", 130, 8, scale=3)

    if message == "stats" and message_timer > 0:
        display.text(
            "Hunger: " + str(byte.hunger),
            10,
            45,
            scale=2
        )
        display.text(
            "Happy: " + str(byte.happiness),
            10,
            70,
            scale=2
        )
        display.text(
            "Energy: " + str(byte.energy),
            10,
            95,
            scale=2
        )
        display.text(
            "Clean: " + str(byte.cleanliness),
            10,
            120,
            scale=2
        )

        message_timer -= 1

    else:
        show_pet_image(pet_state)

        display.set_pen(BLACK)

        if message_timer > 0:
            display.text(message, 105, 155, scale=2)
            message_timer -= 1
        else:
            # display.text(
            #     get_pet_message(pet_state),
            #     85,
            #     155,
            #     scale=2
            # )
            pass

    draw_action_boxes()

    draw_food_icon(first_box_x, box_y)
    draw_play_icon(first_box_x + 62, box_y)
    draw_clean_icon(first_box_x + 124, box_y)
    draw_sleep_icon(first_box_x + 186, box_y)
    draw_stats_icon(first_box_x + 248, box_y)

    display.set_pen(BLUE)
    display.rectangle(
        cursor_x,
        cursor_y,
        cursor_size,
        cursor_size
    )

    display.update()
    sleep(0.02)