#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import RPi.GPIO as GPIO
import time
from threading import Timer

# Constants
MORSE_PIN = 12
DOT = 100  # ms
DASH = 3 * DOT


def millis():
    """ Function which mimics Arduino millis() """
    return int(round(time.time() * 1000))


class MorseButton:
    """ Class to keep track of state variables for a morse code button. """
    def __init__(self, pin, tweet_timeout=3.0):
        """ Store pin, set up IO. """
        self.pin = pin
        self.tweet_timeout = tweet_timeout

        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.pin, GPIO.BOTH,
                              callback=self.callback, bouncetime=15)

        # Set up state variables
        self.time_var = 0
        self.curr_tweet = ""
        self.tweet_started = False

    def print_tweet(self):
        """ Function which prints out the current tweet. """
        print(self.curr_tweet)
        self.curr_tweet = ""
        self.tweet_started = False

    def callback(self, channel):
        """ Callback to handle button rising and falling edges. """
        # Current state of the button is end edge of the transition.
        button_pressed = not GPIO.input(self.pin)

        if button_pressed:  # Button was just pressed.
            duration = millis() - self.time_var

            # If the button was already pressed, record spaces, and restart the
            # tweet printing timer.
            if self.tweet_started:
                if DASH < duration <= 1.5 * DASH:
                    self.curr_tweet += ' '
                elif 1.5 * DASH < duration < 3 * DASH:
                    self.curr_tweet += '  '

                self.tweet_printer.cancel()
                self.tweet_printer = Timer(self.tweet_timeout,
                                           self.print_tweet)
                self.tweet_printer.start()

            # If the tweet was not started, start it, and start the timeout.
            else:
                self.tweet_started = True
                self.tweet_printer = Timer(self.tweet_timeout,
                                           self.print_tweet)
                self.tweet_printer.start()

            self.time_var = millis()  # Keep track of press time.

        else:  # Button was just released.
            duration = millis() - self.time_var

            # Determine if the duration held was a dot or a dash.
            if duration <= 1.5 * DOT:
                self.curr_tweet += '.'
            else:
                self.curr_tweet += '-'

            self.time_var = millis()  # Keep track of release time.


def main():
    button = MorseButton(MORSE_PIN)
    while(True):
        try:
            pass  # Wait for something to happen.
        except KeyboardInterrupt:
            GPIO.cleanup()
            return


if __name__ == '__main__':
    main()
