import curses
import sys
import os
import subprocess
import re

class TipSelector:
    def __init__(self):
        self.options = ["15%", "20%", "25%", "Custom"]
        self.selected = 0
        self.is_custom_selected = False
        self.custom_value = ""
        self.entering_custom = False

def setup_colors():
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_WHITE)   
    curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_WHITE)    
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)     

def draw_button(stdscr, y, x, width, text, is_selected):
    color = curses.color_pair(3) if is_selected else curses.color_pair(1)
    stdscr.attron(color)
    stdscr.addstr(y, x, " " * width)
    stdscr.addstr(y + 1, x, " " * width)
    text_x = x + (width - len(text)) // 2
    stdscr.addstr(y, text_x, text)
    stdscr.attroff(color)

def draw_confirmation(stdscr, message):
    height, width = stdscr.getmaxyx()
    msg_len = len(message)
    y = height // 2
    x = (width - msg_len) // 2
    
    
    stdscr.attron(curses.color_pair(4))
    stdscr.addstr(y-1, x-2, "┌" + "─" * (msg_len+2) + "┐")
    stdscr.addstr(y, x-2, "│ " + message + " │")
    stdscr.addstr(y+1, x-2, "└" + "─" * (msg_len+2) + "┘")
    stdscr.attroff(curses.color_pair(4))
    
    stdscr.addstr(y+2, x, "(y/n)")
    stdscr.refresh()

def draw_tip_prompt(stdscr, selector):
    stdscr.clear()
    
    height, width = stdscr.getmaxyx()
    box_height = 8
    box_width = width - 4
    start_y = (height - box_height) // 2
    start_x = 2

    
    stdscr.attron(curses.color_pair(2))
    stdscr.addstr(start_y, start_x, "╔" + "═" * (box_width-2) + "╗")
    for i in range(1, box_height-1):
        stdscr.addstr(start_y + i, start_x, "║" + " " * (box_width-2) + "║")
    stdscr.addstr(start_y + box_height-1, start_x, "╚" + "═" * (box_width-2) + "╝")
    
    
    title = "Leave a tip?"
    stdscr.addstr(start_y + 1, start_x + (box_width - len(title)) // 2, title)
    
    
    button_width = (box_width - 8) // 3
    
    for i in range(3):
        x_pos = start_x + 2 + i * (button_width + 2)
        is_selected = selector.selected == i and not selector.is_custom_selected
        draw_button(stdscr, start_y + 2, x_pos, button_width, selector.options[i], is_selected)
    
    
    custom_y = start_y + 5
    custom_width = box_width - 4
    custom_text = f"Custom: {selector.custom_value}%" if selector.entering_custom else "Custom"
    is_selected = selector.is_custom_selected
    draw_button(stdscr, custom_y, start_x + 2, custom_width, custom_text, is_selected)
    
    
    if selector.entering_custom:
        hint = "Enter percentage (0-100), Enter to confirm, ESC to cancel"
    else:
        hint = "Use ←↑↓→ arrows to navigate, Enter to select, 'q' to quit"
    stdscr.addstr(height-1, 0, hint, curses.A_DIM)
    
    stdscr.refresh()

def get_tip_value(selector):
    if selector.is_custom_selected:
        try:
            return float(selector.custom_value) if selector.custom_value else 0
        except ValueError:
            return 0
    else:
        return float(selector.options[selector.selected].rstrip('%'))

def handle_custom_input(selector, key):
    if key == 27:  
        selector.entering_custom = False
        selector.custom_value = ""
        return None
    elif key in (10, 13):  
        if selector.custom_value:  
            selector.entering_custom = False
            try:
                value = float(selector.custom_value)
                if value < 8:
                    return "confirm_low"
                return "exit"
            except ValueError:
                selector.custom_value = ""
                return None
    elif key == curses.KEY_BACKSPACE or key == 127:  
        selector.custom_value = selector.custom_value[:-1]
    elif chr(key).isdigit() and len(selector.custom_value) < 3:
        test_value = selector.custom_value + chr(key)
        try:
            value = int(test_value)
            if value <= 100:  
                selector.custom_value = test_value
        except ValueError:
            pass
    return None

def main(stdscr, cmd_args=None):
    curses.curs_set(0)
    setup_colors()
    selector = TipSelector()
    stdscr.keypad(True)
    
    while True:
        draw_tip_prompt(stdscr, selector)
        
        if selector.entering_custom:
            key = stdscr.getch()
            result = handle_custom_input(selector, key)
            if result == "exit":
                return 0
            elif result == "confirm_low":
                draw_confirmation(stdscr, "Are you sure you can't give a better tip?")
                while True:
                    confirm_key = stdscr.getch()
                    if confirm_key in [ord('y'), ord('Y')]:
                        
                        selector.custom_value = ""
                        selector.entering_custom = False
                        break
                    elif confirm_key in [ord('n'), ord('N')]:
                        selector.custom_value = ""
                        selector.entering_custom = False
                        break
            continue
            
        key = stdscr.getch()
        
        if key == ord('q'):
            break
        elif key in [curses.KEY_LEFT, curses.KEY_RIGHT]:
            if selector.is_custom_selected:
                selector.is_custom_selected = False
                selector.selected = 0 if key == curses.KEY_LEFT else 2
            else:
                selector.selected = (selector.selected - 1) % 3 if key == curses.KEY_LEFT else (selector.selected + 1) % 3
        elif key in [curses.KEY_UP, curses.KEY_DOWN]:
            selector.is_custom_selected = not selector.is_custom_selected
            if not selector.is_custom_selected:
                selector.selected = 1
        elif key == 10:  
            if selector.is_custom_selected:
                selector.entering_custom = True
                continue
                
            tip_value = get_tip_value(selector)

    return 0

if __name__ == "__main__":
    if not sys.stdout.isatty():
        print("This program must be run in a terminal")
        sys.exit(1)
    
    cmd_args = sys.argv[1:] if len(sys.argv) > 1 else None
    sys.exit(curses.wrapper(main, cmd_args))