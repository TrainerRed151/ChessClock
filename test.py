#import keyboard
import time
#import curses
from curses import wrapper
import sys


def main(stdscr):
    ns = int(1e9)

    tt = int(sys.argv[1])
    delay = 0
    inc = 0
    if len(sys.argv) > 2:
        extra = int(sys.argv[2])
        if extra < 0:
            delay = -extra*ns
        else:
            inc = extra*ns

    print(inc)

    white_total = tt*60*ns
    black_total = tt*60*ns
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
                if elapsed > delay:
                    white_total -= elapsed
                black_total += inc
            else:
                if elapsed > delay:
                    black_total -= elapsed
                white_total += inc

            white = not white
            start = time.perf_counter_ns()

        time.sleep(0.01)
        elapsed = time.perf_counter_ns() - start

        delay_over = elapsed > delay
        if not delay_over:
            delay_display = ((delay-elapsed)//ns) % 60


        white_display = white_total - elapsed*white*delay_over
        w_display_min = white_display//(60*ns)
        w_display_sec = (white_display//ns) % 60

        black_display = black_total - elapsed*(not white)*delay_over
        b_display_min = black_display//(60*ns)
        b_display_sec = (black_display//ns) % 60

        stdscr.addstr(0, 0, 'White')
        stdscr.addstr(0, 8, 'Black')
        stdscr.addstr(1, 0, f'{w_display_min:02}:{w_display_sec:02}')
        stdscr.addstr(1, 8, f'{b_display_min:02}:{b_display_sec:02}')
        if delay > 0:
            stdscr.addstr(3, 0, f'{delay_display:02}')

        stdscr.refresh()

wrapper(main)
