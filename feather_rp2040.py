import board
import digitalio as dio
from adafruit_seesaw import seesaw, rotaryio, digitalio
from adafruit_ht16k33.segments import Seg7x4
import time


class Clock:
    def __init__(self, display, button_enc, encoder, clock_button):
        self.clock_time = 0
        self.delay_type = 0
        self.delay_time = 0
        self.flagged = False

        self.display = display
        self.button_enc = button_enc
        self.encoder = encoder
        self.clock_button = clock_button
        self.clock_button.switch_to_input(pull=dio.Pull.UP)

    def buttonPushed(self):
        return not self.clock_button.value

    def displayString(self, blink_type=0, setting=False):
        minute = self.clock_time // 60
        second = int(self.clock_time - minute*60)
        deciseconds = int(10*(self.clock_time - minute*60 - second))

        if minute == 0 and not setting:
            return f' {second:02}.{deciseconds}'

        if blink_type == 1:
            return f'  {second:02}'
        elif blink_type == 2:
            return f'{minute:02}  '
        else:
            return f'{minute:02}{second:02}'

    def displayOut(self, blink_type=0, setting=False):
        if self.flagged:
            self.display.blink_rate = 2
            self.display.print('00:00')
        else:
            self.display.print(self.displayString(blink_type=blink_type, setting=setting))

    def setTime(self):
        blink_time = time.monotonic()
        last_position = -self.encoder.position
        minutes = True
        while True:
            position = -self.encoder.position
            tmp_time = time.monotonic() - blink_time
            if tmp_time - int(tmp_time) > 0.5:
                if minutes:
                    self.displayOut(blink_type=1, setting=True)
                else:
                    self.displayOut(blink_type=2, setting=True)
            else:
                self.displayOut(setting=True)

            if position != last_position:
                if minutes:
                    self.clock_time += (position - last_position)*60
                else:
                    self.clock_time += (position - last_position)

                while self.clock_time > 99*60 + 59:
                    if minutes:
                        self.clock_time -= 60
                    else:
                        self.clock_time -= 1

                while self.clock_time < 0:
                    if minutes:
                        self.clock_time += 60
                    else:
                        self.clock_time += 1

                last_position = position

            if not self.button_enc.value:
                while not self.button_enc.value:
                    pass

                time.sleep(0.1)
                if not minutes:
                    break

                minutes = False

        self.clock_time += 0.001
        self.displayOut(setting=True)


class Game:
    def __init__(self):
        i2c = board.STEMMA_I2C()  # For using the built-in STEMMA QT connector on a microcontroller
        rotary = seesaw.Seesaw(i2c, addr=0x36)
        rotary.pin_mode(24, rotary.INPUT_PULLUP)

        self.button_enc = digitalio.DigitalIO(rotary, 24)
        self.encoder = rotaryio.IncrementalEncoder(rotary)

        self.left = Clock(Seg7x4(i2c, address=0x70), self.button_enc, self.encoder, dio.DigitalInOut(board.D9))
        self.right = Clock(Seg7x4(i2c, address=0x71), self.button_enc, self.encoder, dio.DigitalInOut(board.D11))

        self.turn = 0

    def setUp(self):
        self.left.display.colon = True
        self.right.display.colon = True
        self.left.displayOut(setting=True)
        self.right.displayOut(setting=True)

        self.left.setTime()
        self.right.setTime()

    def runGame(self):
        end_of_game = False

        while True:
            if self.left.buttonPushed():
                self.turn = 1
                break

            if self.right.buttonPushed():
                self.turn = 0
                break

        while not end_of_game:
            side = self.left if self.turn else self.right
            ref_time = time.monotonic()
            start_time = side.clock_time
            while True:
                spent_time = time.monotonic() - ref_time
                side.clock_time = start_time - spent_time
                side.display.colon = (spent_time - int(spent_time) > 0.5) and (side.clock_time >= 60)

                side.displayOut()

                if side.clock_time <= 0:
                    end_of_game = True
                    side.blink_rate = 2
                    side.flagged = True
                    side.displayOut()
                    break

                if side.buttonPushed():
                    self.turn = not self.turn
                    side.display.colon = side.clock_time >= 60
                    break

                # pause logic
                if not self.button_enc.value:
                    time.sleep(0.1)

                    while not self.button_enc.value:
                        pass

                    while self.button_enc.value:
                        pass

                    while not self.button_enc.value:
                        pass

                    sleep(0.1)
                    break

        self.endGame()

    def endGame(self):
        while True:
            pass


def main():
    game = Game()
    game.setUp()
    game.runGame()


main()
