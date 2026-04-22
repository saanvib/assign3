#!/usr/bin/env python3
import unittest
import os
import sys
import argparse
import subprocess
import unittest
import urllib.request


class TestChorusLapilli(unittest.TestCase):
    '''Integration testing for Chorus Lapilli

    This class handles the entire react start up, testing, and take down
    process. Feel free to modify it to suit your needs.
    '''

    # ========================== [USEFUL CONSTANTS] ===========================

    # Vite default startup address
    VITE_HOST_ADDR = 'http://localhost:5173'

    # XPATH query used to find Chorus Lapilli board tiles
    BOARD_TILE_XPATH = '//button[contains(@class, \'square\')]'

    # Sets of symbol classes - each string contains all valid characters
    # for that particular symbol
    SYMBOL_BLANK = ''
    SYMBOL_X = 'Xx'
    SYMBOL_O = '0Oo'

    # ======================== [SETUP/TEARDOWN HOOKS] =========================

    @classmethod
    def setUpClass(cls):
        '''This function runs before testing occurs.

        Bring up the web app and configure Selenium
        '''

        env = dict(os.environ)
        env.update({
            # Prevent React from starting its own browser window
            'BROWSER': 'none',
        })

        subprocess.run(['npm', 'install'],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL,
                           env=env,
                           check=True)

        # Await Webserver Start
        cls.vite = subprocess.Popen(
            ['npm', 'run', 'dev'],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env)

        if cls.vite.stdout is None:
            raise OSError("Vite failed to start")
        for _ in cls.vite.stdout:
            try:
                with urllib.request.urlopen(cls.VITE_HOST_ADDR):
                    break

            except IOError:
                pass

            # Ensure Vite does not terminate early
            if cls.vite.poll() is not None:
                raise OSError('Vite terminated before test')
        if cls.vite.poll() is not None:
            raise OSError('Vite terminated before test')

        cls.driver = Browser()
        cls.driver.get(cls.VITE_HOST_ADDR)
        cls.driver.implicitly_wait(0.5)

    @classmethod
    def tearDownClass(cls):
        '''This function runs after all testing have run.

        Terminate Vite and take down the Selenium webdriver.
        '''
        cls.vite.terminate()
        cls.vite.wait()
        cls.driver.quit()

    def setUp(self):
        '''This function runs before every test.

        Refresh the browser so we get a new board.
        '''
        self.driver.refresh()

    def tearDown(self):
        '''This function runs after every test.

        Not needed, but feel free to add stuff here.
        '''

    # ========================== [HELPER FUNCTIONS] ===========================

    def assertBoardEmpty(self, tiles):
        '''Checks if all board tiles are empty.

        Arguments:
          tiles: List[WebElement] - a board consisting of 9 buttons elements
        '''
        if len(tiles) != 9:
            raise AssertionError('tiles is not a 3x3 grid')
        for i, tile in enumerate(tiles):
            if tile.text.strip():
                raise AssertionError(f'tile {i} is not empty: '
                                     f'\'{tile.text}\'')

    def assertTileIs(self, tile, symbol_set):
        '''Checks if a certain tile has a certain symbol.

        Arguments:
          tile: WebElement - the button element to check
          symbol_set: str - a string containing all the valid symbols
        Raises:
          AssertionError - if tile is not in the symbol set
        '''
        if symbol_set is None:
            return
        if symbol_set == self.SYMBOL_BLANK:
            name = 'BLANK'
        elif symbol_set == self.SYMBOL_X:
            name = 'X'
        elif symbol_set == self.SYMBOL_O:
            name = 'O'
        else:
            name = 'in symbol_set'
        text = tile.text.strip()
        if ((symbol_set == self.SYMBOL_BLANK and text)
                or (symbol_set != self.SYMBOL_BLANK and not text)
                or text not in symbol_set):
            raise AssertionError(f'tile is not {name}: \'{tile.text}\'')


# =========================== [ADD YOUR TESTS HERE] ===========================

    def test_new_board_empty(self):
        '''Check if a new game always starts with an empty board.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertBoardEmpty(tiles)

    def test_button_click(self):
        '''Check if clicking the top-left button adds an X.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        self.assertTileIs(tiles[0], self.SYMBOL_BLANK)
        tiles[0].click()
        self.assertTileIs(tiles[0], self.SYMBOL_X)

    def test_no_more_moves_after_win(self):
        '''Check that clicking tiles does nothing after a player wins.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        # X takes top row (0,1,2); O takes 3,4 - X wins after tile 2
        tiles[0].click()  # X
        tiles[3].click()  # O
        tiles[1].click()  # X
        tiles[4].click()  # O
        tiles[2].click()  # X wins with 0,1,2
        # Click an empty tile - must remain empty
        tiles[5].click()
        self.assertTileIs(tiles[5], self.SYMBOL_BLANK)

    def test_player_alternation(self):
        '''Check that X and O alternate on each click.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        tiles[0].click()  # X
        tiles[1].click()  # O
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        self.assertTileIs(tiles[1], self.SYMBOL_O)

    def test_no_overwrite_occupied_tile(self):
        '''Check that clicking an already-occupied tile does not change it.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        tiles[0].click()  # X placed at 0
        tiles[0].click()  # O tries to click same tile - should be ignored
        self.assertTileIs(tiles[0], self.SYMBOL_X)

    def test_move_phase_invalid_destination_reverts(self):
        '''Check that an invalid move destination in move phase clears selection.'''
        tiles = self.driver.find_elements(By.XPATH, self.BOARD_TILE_XPATH)
        # Place X at 0,1,3 and O at 2,5,7 (no winner)
        tiles[0].click()  # X
        tiles[2].click()  # O
        tiles[1].click()  # X
        tiles[5].click()  # O
        tiles[3].click()  # X - 3 pieces placed, enters move phase
        tiles[7].click()  # O - 3 pieces placed
        # X is in move phase. Select X at 0, then click tile 8 (not adjacent to 0)
        tiles[0].click()  # select X at 0
        tiles[8].click()  # invalid: not adjacent, should revert
        # X at 0 must still be there and 8 must still be empty
        self.assertTileIs(tiles[0], self.SYMBOL_X)
        self.assertTileIs(tiles[8], self.SYMBOL_BLANK)


# ================= [DO NOT MAKE ANY CHANGES BELOW THIS LINE] =================

if __name__ != '__main__':
    from selenium.webdriver import Firefox as Browser
    from selenium.webdriver.common.by import By
else:
    parser = argparse.ArgumentParser(prog=sys.argv[0],
                                     description='Chorus Lapilli Tester')
    parser.add_argument('-b',
                        '--browser',
                        action='store',
                        metavar='name',
                        choices=['firefox', 'chrome', 'safari'],
                        default='firefox',
                        help='the browser to run tests with')
    parser.add_argument('-c',
                        '--change-dir',
                        action='store',
                        metavar='dir',
                        default=None,
                        help=('change the working directory before running '
                              'tests'))

    # Change the working directory
    options = parser.parse_args(sys.argv[1:])
    # Import different browser drivers based on user selection
    try:
        if options.browser == 'firefox':
            from selenium.webdriver import Firefox as Browser
        elif options.browser == 'chrome':
            from selenium.webdriver import Chrome as Browser
        else:
            from selenium.webdriver import Safari as Browser
        from selenium.webdriver.common.by import By
    except ImportError as err:
        print('[Error]',
              err, '\n\n'
              'Please refer to the Selenium documentation on installing the '
              'webdriver:\n'
              'https://www.selenium.dev/documentation/webdriver/'
              'getting_started/',
              file=sys.stderr)
        sys.exit(1)

    if options.change_dir:
        try:
            os.chdir(options.change_dir)
        except OSError as err:
            print(err, file=sys.stderr)
            sys.exit(1)

    if not os.path.isfile('package.json'):
        print('Invalid directory: cannot find \'package.json\'',
              file=sys.stderr)
        sys.exit(1)

    tests = unittest.defaultTestLoader.loadTestsFromTestCase(TestChorusLapilli)
    unittest.TextTestRunner().run(tests)
