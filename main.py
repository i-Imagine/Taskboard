import pygame as pg
# from datetime import date, datetime
from os import listdir, path, environ

from pygame.image import load

from fileio import Settings, fileread, filewrite
from mathfunctions import solve_stack
from timefunctions import get_int_24h_time

environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (0, 30)
pg.init()
fileread()


def load_image(relative_path_ls, transform_tuple=None, alpha=False):
    '''Given a list form filepath, loads and converts the image given and transforms size if requested.'''
    uncoverted = pg.image.load(path.join(*relative_path_ls)) # Asterisks unpacks iterable so OS path system can handle it.
    if alpha:
        converted = uncoverted.convert_alpha()
    else:
        converted = uncoverted.convert()
    if transform_tuple != None:
        converted = pg.transform.scale(converted, transform_tuple)
    return converted


# Determine the largest appropriate window size using the screen resolution. 
SCREEN_INFO = pg.display.Info()
WIDTH, HEIGHT = SCREEN_INFO.current_w, SCREEN_INFO.current_h - 70 # Offset for the window's title bar.
WIN = pg.display.set_mode((WIDTH, HEIGHT))
# Customise the title bar.
pg.display.set_caption("Taskboard")
ICON = load_image(["assets", "tasks_icon.png"])
pg.display.set_icon(ICON)

# Colours.
WHITE = (255, 255, 255)
PALE_GREY = (243, 243, 243)
LIGHT_GREY = (217, 217, 217)
DARK_GREY = (128, 128, 128)
BLACK_GREY = (52, 58, 64) # (73, 80, 87)
BLACK = (33, 37, 41)
BLACK_GREEN = (19, 42, 19) 
DARK_GREEN = (49, 87, 44)
GREEN = (79, 119, 45)
LIGHT_GREEN = (144, 169, 85)
PALE_GREEN = (236, 243, 158)
RED = (232, 17, 35)

# Initiate element construction constants.
ELEMENT_PADDING = 40
S_ELEMENT_PADDING = 30
BORDER_PADDING = 10
BUTTON_LENGTH = 50
NAV_BAR_HEIGHT = 75
NAV_BAR_BORDER_HEIGHT = 5
INFO_PANEL_H_SCALE = 1/4
TIME_GLASS_TITLE_HEIGHT = 30
TIME_GLASS_WIDTH = 90
TIME_GLASS_BG_WIDTH = 220
INNER_TIME_GLASS_HEIGHT = HEIGHT - NAV_BAR_HEIGHT - 2*S_ELEMENT_PADDING - TIME_GLASS_TITLE_HEIGHT - 2*BORDER_PADDING - 2*ELEMENT_PADDING - TIME_GLASS_WIDTH # Overtime square same height as glass width.
SHADOW_DEPTH = 10
# Initiate other constants.
THEME_CHANGE_TIMES = (700, 1700)
FPS = 10

# Load sprites.
SHADOW_TEMPLATE = load_image(["assets", "shadow.png"], alpha=True)
TIME_FLUID_IMAGE = load_image(["assets", "timeleft.jpg"], (TIME_GLASS_WIDTH - 2*BORDER_PADDING, INNER_TIME_GLASS_HEIGHT))
OVERTIME_IMAGE = load_image(["assets", "overtime.jpg"], (TIME_GLASS_WIDTH - 2*BORDER_PADDING, TIME_GLASS_WIDTH - 2*BORDER_PADDING))
LOG = load_image(["assets", "mylog.png"], (64, 64), alpha=True)
LOG_F = load_image(["assets", "mylogflipped.png"], (128, 64), alpha=True)
# Load elements.
INT_TIME_SCENERY_LS = sorted([int(s.rstrip(".png")) for s in listdir(path.join("assets", "bg"))])
nav_bar = pg.Surface((WIDTH, NAV_BAR_HEIGHT))
NAV_BAR_BORDER = pg.Surface((WIDTH, NAV_BAR_BORDER_HEIGHT))
quit_button = pg.Rect(WIDTH - BUTTON_LENGTH - BORDER_PADDING, BORDER_PADDING, BUTTON_LENGTH, BUTTON_LENGTH)
resize_button = quit_button.move(-BUTTON_LENGTH - BORDER_PADDING, 0)
minimise_button = resize_button.move(-BUTTON_LENGTH - BORDER_PADDING, 0)
info_panel = pg.Surface((WIDTH/3, HEIGHT*INFO_PANEL_H_SCALE - NAV_BAR_HEIGHT))
time_glass_canvas = pg.Surface((TIME_GLASS_BG_WIDTH, HEIGHT - NAV_BAR_HEIGHT))
time_glass = pg.Surface((TIME_GLASS_WIDTH, INNER_TIME_GLASS_HEIGHT + 2*BORDER_PADDING))
time_glass_marker = pg.Surface((TIME_GLASS_WIDTH + BORDER_PADDING, BORDER_PADDING))
overtime_glass = pg.Surface((TIME_GLASS_WIDTH, TIME_GLASS_WIDTH))



def proportional_scaling_tuple(surface, request_type, scale_factor=1, dx=0, dy=0):
    '''Returns a tuple with the correct x and y lengths to create a proportionally scaled image.
    Requests can be: to_screen_x, to_screen_y, multiplier'''
    old_width, old_height = surface.get_width(), surface.get_height()
    match request_type.lower():
        case "to_screen_x":
            x = WIDTH*scale_factor + dx
            y = old_height*(x/old_width) # The enlargement ratio.
        case "to_screen_y":
            y = HEIGHT*scale_factor + dy
            x = old_width*(y/old_height) # The enlargement ratio.
        case "multiplier":
            x, y = old_width*scale_factor, old_height*scale_factor
    return (x, y)


def centre_crop(surface, x_len, y_len, dx=0, dy=0):
    '''Completes a centred crop on the given surface to the given dimensions and returns it.'''
    crop_canvas = pg.Surface((x_len, y_len))
    # Get coordinate of final crop's top right corner in uncropped image. 
    x_origin = 0.5*surface.get_width() - 0.5*x_len
    y_origin = 0.5*surface.get_height() - 0.5*y_len
    crop_canvas.blit(surface, (0, 0), (x_origin + dx, y_origin + dy, x_len, y_len)) # (a, b, c, d) is crop shape sized c by d starting with (a, b) as top left. 
    return crop_canvas


# def top_crop(surface, x_len, y_len, dx=0, dy=0):
#     '''Completes a crop from top to bottom on the given surface to the given dimensions and returns it.'''
#     crop_canvas = pg.Surface((x_len, y_len))
#     # Get coordinate of final crop's top right corner in uncropped image. 
#     x_origin = 0.5*surface.get_width() - 0.5*x_len
#     y_origin = surface.get_height() - y_len
#     crop_canvas.blit(surface, (0, 0), ())

def draw_shadow(length, depth=20, light_from="north"):
    '''Draws and returns a shadow of the given length of depth, facing the given direction.'''
    scaled_shadow = pg.transform.scale(SHADOW_TEMPLATE, (length, depth))
    match light_from.lower():
        case "north":
            deg_rotation = 180
        case "east":
            deg_rotation = 90
        case "south":
            deg_rotation = 0
        case "west":
            deg_rotation = 270
    return pg.transform.rotate(scaled_shadow, deg_rotation)


def get_theme():
    '''Determines whether the program should be in dark or light theme depending on settings and time.'''
    if Settings.natural_dark_theme_change == True:
        if THEME_CHANGE_TIMES[0] < get_int_24h_time() < THEME_CHANGE_TIMES[1]:
            current_dark_theme = False
        else:
            current_dark_theme = True
    elif Settings.always_dark_theme == True:
        current_dark_theme = True
    else: # Always light theme.
        current_dark_theme = False
    return current_dark_theme

def get_scenery():
    '''Returns the correct scenery surface according to the current time.'''
    now = get_int_24h_time()
    # Get the image whose time was most recently past.
    latest_time = 0
    for k in INT_TIME_SCENERY_LS:
        if now > k:
            latest_time = k
        else:
            break
    if latest_time < 1000:
        latest_time = "0" + str(latest_time)
    else:
        latest_time= str(latest_time)
    return load_image(["assets", "bg", ".".join((latest_time, "png"))])


def triangle_stacker(number, surface, x_leftmost, y_bottommost, dx_adjacent, dy_adjacent, dx_rows, dy_rows):
    '''Creates a 'blits' ready iterable containing 'number' of 'surface' stacked in a triangle, with remainders on one side.'''
    # Determine the side length and remainders when arranging the number into a triangle.
    remaining_rows, remaining_singles = solve_stack(number)
    num_comp_rows = 0
    stack = []
    while num_comp_rows < remaining_rows:
        comp_in_row = 0
        # Check if there is a remainder to append onto this row.
        if remaining_singles > 0:
            remaining_singles -= 1
            appended_remainder = 1
        else:
            appended_remainder = 0
        # Append the number of logs in the row onto the iterable in the correct order and location.
        while comp_in_row < remaining_rows - num_comp_rows + appended_remainder:
            stack.append((surface,(
                x_leftmost + dx_adjacent*comp_in_row + dx_rows*num_comp_rows,
                y_bottommost + dy_adjacent*comp_in_row - dy_rows*num_comp_rows
            )))
            comp_in_row += 1
        num_comp_rows += 1
    return stack


def jenga_stacker(number, surface, f_surface, tower_num, x_leftmost, y_bottommost, dx_adjacent, dy_adjacent, dx_rows, dy_rows, jenga_dx):
    '''Creates a 'blits' ready iterable containing 'number' of 'surface' stacked like a jenga tower.'''
    # Determine the side length and remainders when arranging the number into a triangle.
    if f_surface == None:
        f_surface = pg.transform.flip(surface, True, False)
    rows = number // (tower_num*5) + (number % (tower_num*5) > 0)
    number_left = number
    num_comp_rows = 0
    stack = []
    while num_comp_rows < rows:
        comp_in_row = 0
        row_stack = []
        if num_comp_rows % 2 == 0:
            flipped = False
            current_surf = surface
            flip_only_rows_dx = 0
            row_adjusted_adjacent_dx = dx_adjacent
            row_adjusted_adjacent_dy = dy_adjacent
        else:
            flipped = True
            current_surf = f_surface
            flip_only_rows_dx = dx_rows
            row_adjusted_adjacent_dx = dx_adjacent * 0.3
            row_adjusted_adjacent_dy = dy_adjacent * -5
        # Append the number of logs in the row onto the iterable in the correct order and location.
        while comp_in_row < (tower_num*5) and number_left > 0:
            if flipped:
                tower_dx = jenga_dx * (comp_in_row // 5)
                separate_tower_d = comp_in_row -  comp_in_row % 5 
            else:
                tower_dx = 0
                separate_tower_d = 0
            row_stack.append((current_surf,(
                x_leftmost + row_adjusted_adjacent_dx*(comp_in_row - separate_tower_d*0.7) + tower_dx + flip_only_rows_dx,
                y_bottommost + row_adjusted_adjacent_dy*(comp_in_row - separate_tower_d) + separate_tower_d*(dy_adjacent) - dy_rows*num_comp_rows
            )))
            comp_in_row += 1
            number_left -= 1
            if comp_in_row % 5 == 0 and flipped:
                stack.extend(sorted(row_stack, reverse=True))
                row_stack = []
            # print(number_left)

        if number_left == 0 and flipped:
            stack.extend(sorted(row_stack, reverse=True))
        elif not flipped:
            stack.extend(row_stack)
        num_comp_rows += 1
        # print(num_comp_rows, rows)
    return stack


def draw_scenery():
    '''Redraws all elements of the scenery and returns the updated version.'''
    # Scale and crop the correct image into the correct shape and size.
    raw_scenery = get_scenery()
    scaled_scenery = pg.transform.scale(raw_scenery, proportional_scaling_tuple(raw_scenery, "to_screen_y", scale_factor=1-INFO_PANEL_H_SCALE))
    resized_scenery = centre_crop(scaled_scenery, WIDTH/3, HEIGHT*(1-INFO_PANEL_H_SCALE), dx=-50)
    # Add other elements.
    resized_scenery.blit(draw_shadow(WIDTH/3, SHADOW_DEPTH, "south"), (0, 0))
    # Fire
    x_stack, y_stack = WIDTH/3/5, HEIGHT - HEIGHT*INFO_PANEL_H_SCALE - HEIGHT/10
    adjacent_dx, adjacent_dy = 23, 1
    row_dx, row_dy = 10, 23
    resized_scenery.blits(triangle_stacker(130, LOG, x_stack, y_stack, adjacent_dx, adjacent_dy, row_dx, row_dy))
    # Chicken?
    return resized_scenery


def draw_info_panel():
    ''''''



def draw_time_glass(canvas_colour, border_colour, glass_bg_colour):
    '''Redraws all elements of the time glass and returns the updated version.'''
    # Draw up the full panel, the time glass, and its border. 
    time_glass_canvas.fill(canvas_colour)
    time_glass.fill(border_colour)
    time_glass.blit(TIME_FLUID_IMAGE, (BORDER_PADDING, BORDER_PADDING))

    # Determine how much time is left, or if it is currently overtime.
    current_hours = get_int_24h_time(h_min_decimal=True)
    work_start, work_end = Settings.working_hours
    if current_hours > work_end or current_hours < work_start:
        current_hours = work_end
        overtime = True
    else:
        overtime = False
    time_past_fraction = (current_hours - work_start)/(work_end - work_start)
    # Block out past time.
    time_glass.fill(glass_bg_colour, (
        # (a, b, c, d) is filling a shape sized c by d starting with (a, b) as top left.
        BORDER_PADDING, BORDER_PADDING,
        TIME_GLASS_WIDTH - 2*BORDER_PADDING, time_past_fraction*INNER_TIME_GLASS_HEIGHT
    ))

    time_glass_canvas.blit(time_glass, (ELEMENT_PADDING + SHADOW_DEPTH, 2*S_ELEMENT_PADDING + TIME_GLASS_TITLE_HEIGHT))

    # Blit in marker bars over the time glass.
    time_glass_marker.fill(border_colour)
    marker_num_inclusive = 5
    marker_heights_from_glass = [n/(marker_num_inclusive - 1) * (INNER_TIME_GLASS_HEIGHT + BORDER_PADDING) for n in range(marker_num_inclusive)]
    for h in marker_heights_from_glass:
        time_glass_canvas.blit(time_glass_marker, (ELEMENT_PADDING + SHADOW_DEPTH, h + 2*S_ELEMENT_PADDING + TIME_GLASS_TITLE_HEIGHT))

    # MARKER TEXT

    # TITLE

    # Draw the overtime glass and fill it if currently in overtime.
    overtime_glass.fill(border_colour)
    if overtime:
        overtime_glass.blit(OVERTIME_IMAGE, (BORDER_PADDING, BORDER_PADDING))
    else:
        overtime_glass.fill(glass_bg_colour, (BORDER_PADDING, BORDER_PADDING, TIME_GLASS_WIDTH - 2*BORDER_PADDING, TIME_GLASS_WIDTH - 2*BORDER_PADDING))
    time_glass_canvas.blit(overtime_glass, (ELEMENT_PADDING + SHADOW_DEPTH, 2*S_ELEMENT_PADDING + TIME_GLASS_TITLE_HEIGHT + 2*BORDER_PADDING + INNER_TIME_GLASS_HEIGHT + ELEMENT_PADDING))

    # OVERTIME TEXT

    return time_glass_canvas


def draw_nav_bar(mouse_pos, bar_colour, feature_colour, caution_colour):
    '''Redraws all elements of the navigation bar and returns the updated version.'''
    nav_bar.fill(bar_colour)
    NAV_BAR_BORDER.fill(feature_colour)
    nav_bar.blit(NAV_BAR_BORDER, (0, NAV_BAR_HEIGHT - NAV_BAR_BORDER_HEIGHT))
    
    # Buttons

    return nav_bar

def draw_window():
    ''''''


'''     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.     .-.
   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   `._.'   '''


def main():
    refresh_timer = float("inf")
    previous_theme = None

    clock = pg.time.Clock()
    running = True

    while running:
        clock.tick(FPS)
        mouse_location = pg.mouse.get_pos()
        # Detect user input.
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            if event.type == pg.MOUSEBUTTONUP:
                pass

        refresh_timer += clock.get_time()
        # Recheck background and colour theme depending on current time every 5 minutes.
        if refresh_timer > 1000 * 60 * 5:
            refresh_timer = 0

            current_dark_theme = get_theme()
            if previous_theme != current_dark_theme:
                previous_theme = current_dark_theme
                if current_dark_theme:
                    bg_colour = BLACK_GREY
                    other_bg_colour = DARK_GREY
                    opposite_bg_colour = LIGHT_GREY
                    contrast_colour = WHITE
                    opposite_contrast_colour = BLACK
                    splash_colour = LIGHT_GREEN
                    splash_text_colour = BLACK_GREEN
                    accent_colour = GREEN
                    warning_colour = RED
                else:
                    bg_colour = PALE_GREY
                    other_bg_colour = LIGHT_GREY
                    opposite_bg_colour = DARK_GREY
                    contrast_colour = BLACK
                    opposite_contrast_colour = WHITE
                    splash_colour = DARK_GREEN
                    splash_text_colour = PALE_GREEN
                    accent_colour = GREEN
                    warning_colour = RED
            
            # Draw up panels that are not interactable and rarely update.
            current_scenery = draw_scenery()
            current_time_glass = draw_time_glass(other_bg_colour, opposite_contrast_colour, opposite_bg_colour)


        # Draw up panels that are interactive.
        current_nav_bar = draw_nav_bar(mouse_location, splash_colour, accent_colour, warning_colour)
        info_panel.fill(other_bg_colour)

        # Background elements.
        

        # Fill in the screen.
        WIN.fill(bg_colour)
        WIN.blit(current_scenery, (0, HEIGHT*INFO_PANEL_H_SCALE))
        WIN.blit(info_panel, (0, NAV_BAR_HEIGHT))
        WIN.blit(current_time_glass, (WIDTH - TIME_GLASS_BG_WIDTH, NAV_BAR_HEIGHT))

        WIN.blit(current_nav_bar, (0, 0))

        # Drop shadows.
        WIN.blit(draw_shadow(HEIGHT, SHADOW_DEPTH, "east"), (WIDTH - TIME_GLASS_BG_WIDTH, 0))
        WIN.blit(draw_shadow(HEIGHT, SHADOW_DEPTH, "west"), (WIDTH/3 - SHADOW_DEPTH, 0))
        


        
        # WIN.blits(jenga_stacker(30, LOG, LOG_F, 2, x_stack - 500, y_stack, adjacent_dx + 4, adjacent_dy, row_dx, row_dy, 120))

        pg.display.update()

    # User has quit.
    filewrite()
    pg.quit()


if __name__ == "__main__":
    main()