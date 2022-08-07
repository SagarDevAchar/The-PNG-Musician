import os

import cv2
import numpy as np
from os import listdir
from tqdm import trange
import subprocess
import msvcrt


def parse_stegano_or(arr: np.array):
    arr = np.reshape(arr, (1, W * H * D))
    sp = np.where(arr != 0)[1][0]
    bits = W * H * D - sp

    mp3 = []
    for b in trange(0, bits, 4, ncols=100, unit=' bytes'):
        mp3.append((arr[0, sp+b+0] << 6) | (arr[0, sp+b+1] << 4) | (arr[0, sp+b+2] << 2) | (arr[0, sp+b+3] << 0))

    return bytes(mp3)


def print_ascii_image(img: np.array, norm=False):
    LEVELS = ['  ', '░░', '▒▒', '▓▓', '██']

    if norm:
        img = np.array(np.array(img / img.max(), dtype=np.float) * 4, dtype=np.uint8)
    else:
        img //= 63
    borderW = img.shape[1] * 2

    print(" ╔" + "╦" * borderW + "╗")
    for row in img:
        print(end=' ╠')
        for pixel in row:
            print(LEVELS[pixel], end='')
        print('╣')
    print(" ╚" + "╩" * borderW + "╝")


if __name__ == '__main__':
    while True:
        SECTION_SEPERATOR = '\n' + '-' * 200 + '\n'

        LOGO = """
                                            ████████╗██╗  ██╗███████╗    ██████╗ ███╗   ██╗ ██████╗     ███╗   ███╗██╗   ██╗███████╗██╗ ██████╗██╗ █████╗ ███╗   ██╗
                                            ╚══██╔══╝██║  ██║██╔════╝    ██╔══██╗████╗  ██║██╔════╝     ████╗ ████║██║   ██║██╔════╝██║██╔════╝██║██╔══██╗████╗  ██║
                                               ██║   ███████║█████╗      ██████╔╝██╔██╗ ██║██║  ███╗    ██╔████╔██║██║   ██║███████╗██║██║     ██║███████║██╔██╗ ██║
                                               ██║   ██╔══██║██╔══╝      ██╔═══╝ ██║╚██╗██║██║   ██║    ██║╚██╔╝██║██║   ██║╚════██║██║██║     ██║██╔══██║██║╚██╗██║
                                               ██║   ██║  ██║███████╗    ██║     ██║ ╚████║╚██████╔╝    ██║ ╚═╝ ██║╚██████╔╝███████║██║╚██████╗██║██║  ██║██║ ╚████║
                                               ╚═╝   ╚═╝  ╚═╝╚══════╝    ╚═╝     ╚═╝  ╚═══╝ ╚═════╝     ╚═╝     ╚═╝ ╚═════╝ ╚══════╝╚═╝ ╚═════╝╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
                                                                                                                                                                    
                                                                     █▀▄ █ █   █▀▀ █▀█ █▀▀ █▀█ █▀▄   █▀▄ █▀▀ █ █   █▀█ █▀▀ █ █ █▀█ █▀▄
                                                                     █▀▄  █    ▀▀█ █▀█ █ █ █▀█ █▀▄   █ █ █▀▀ ▀▄▀   █▀█ █   █▀█ █▀█ █▀▄
                                                                     ▀▀   ▀    ▀▀▀ ▀ ▀ ▀▀▀ ▀ ▀ ▀ ▀   ▀▀  ▀▀▀  ▀    ▀ ▀ ▀▀▀ ▀ ▀ ▀ ▀ ▀ ▀
        """ + SECTION_SEPERATOR

        print(LOGO)

        print("Hey There!\nI'm THE PNG MUSICIAN!")
        print("I convert PNG Images to MP3 Audio and play them!")
        print("\nWell that's not exactly how I work, but it's one way to put it :P")
        print("\nAnyways, maximize this window for the best experience ;)")

        print(SECTION_SEPERATOR)

        try:
            file_list = listdir('SRC')
            png_file_list = []
            for filename in file_list:
                if filename[-4:] == '.png':
                    png_file_list.append(filename)

            print("I found %d PNG files!\nWhich one do you want me to play?" % len(png_file_list))
            for png_file in png_file_list:
                print(f'\t{png_file_list.index(png_file)+1:2d}) {png_file:s}')

            file_index = -1
            while True:
                try:
                    file_index = int(input('\nEnter an image number: ').strip())
                    if 0 < file_index <= len(png_file_list):
                        file_index -= 1
                        break
                    else:
                        raise ValueError
                except Exception:
                    print("Hmmm, that's not quite what I expected. How about you give it another try!")
            SONG_NAME = png_file_list[file_index]

            print(SECTION_SEPERATOR)

            print("Reading Image...")
            STEGANO_IMAGE = cv2.imread(fr'SRC\{SONG_NAME:s}', cv2.IMREAD_COLOR)
            H, W, D = STEGANO_IMAGE.shape

            print("Creating Music from the Image...")
            MP3_DATA = parse_stegano_or(STEGANO_IMAGE & 0x3)

            print("Writing Music to out.mp3...")
            with open('out.mp3', 'wb') as mp3_file:
                mp3_file.write(MP3_DATA)

            print(SECTION_SEPERATOR)

            print("{:^200s}".format(f"Currently Playing {SONG_NAME}\n"))
            ascii_image_w = (len(SECTION_SEPERATOR) - 6) // 2
            ascii_image_h = ascii_image_w * 9 // 16
            print_ascii_image(cv2.cvtColor(cv2.resize(STEGANO_IMAGE, (ascii_image_w, ascii_image_h)), cv2.COLOR_BGR2GRAY))
            print('')

            player_subprocess = subprocess.Popen(['bin/mpg123', '-q', 'out.mp3'])

            print("{:^200s}".format('Press ENTER to stop playing the song'), end='')
            while player_subprocess.poll() is None:
                if msvcrt.kbhit():
                    if msvcrt.getch() == b'\r':
                        break
            print("\r{:^200s}".format('Finished Playing!'))

            player_subprocess.kill()

        except FileNotFoundError:
            print("Looks like you have lost the 'bin' or 'SRC' folder!\nUnfortunately, I cannot work without those...")

        print(SECTION_SEPERATOR)
        input("Press ENTER to start over")
        os.system('cls')
