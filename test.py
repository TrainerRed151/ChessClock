#import keyboard
import time
#import curses
from curses import wrapper


def main(stdscr):
    ns = int(1e9)

    white_total = 5*60*ns
    black_total = 5*60*ns
    white_display = white_total
    black_display = black_total
    white = True

    stdscr.nodelay(True)
    stdscr.clear()

    start = time.perf_counter_ns()
    elapsed = 0
    while white_display > 0 and black_display > 0:
        if stdscr.getch() == ord('a'):
            if white:
                white_total -= elapsed
            else:
                black_total -= elapsed

            white = not white
            start = time.perf_counter_ns()

        time.sleep(0.01)
        elapsed = time.perf_counter_ns() - start

        white_display = white_total - elapsed*white
        w_display_min = white_display//(60*ns)
        w_display_sec = (white_display//ns) % 60

        black_display = black_total - elapsed*(not white)
        b_display_min = black_display//(60*ns)
        b_display_sec = (black_display//ns) % 60

        stdscr.addstr(0, 0, 'White')
        stdscr.addstr(0, 8, 'Black')
        stdscr.addstr(1, 0, f'{w_display_min:02}:{w_display_sec:02}')
        stdscr.addstr(1, 8, f'{b_display_min:02}:{b_display_sec:02}')
        stdscr.refresh()

wrapper(main)
