from requests import get
from zipfile import ZipFile
from sys import argv
from os import remove, mkdir, path, system, listdir
from shutil import move, rmtree


def createProject():
    r = get("https://api.github.com/repos/libsdl-org/SDL/releases/latest")

    print("Retrieving SDL2 download URL")
    for i in r.json()["assets"]:
        for k, v in i.items():
            if k == "browser_download_url" and "mingw.zip" in v:
                print(v)
                sdl_zip_url = v

    print("Downloading SDL2 zip archive")
    r = get(sdl_zip_url, stream = True)
    with open("SDL2.zip", "wb") as f:
        for chunk in r.iter_content(chunk_size = 1024):
            f.write(chunk)

    print("Extracting SDL2.zip")
    with ZipFile("SDL2.zip", "r") as f:
        f.extractall()

    remove("SDL2.zip")

    folders = ["assets", "build", "include", "libs", "src"]
    for folder in folders:
        if path.exists(folder):
            rmtree(folder)
        mkdir(folder)
        print(f"Created folder '{folder}'")

    move("SDL2-2.24.0/x86_64-w64-mingw32/bin/SDL2.dll", "build/SDL2.dll")
    move("SDL2-2.24.0/x86_64-w64-mingw32/include/SDL2", "include/SDL2")
    move("SDL2-2.24.0/x86_64-w64-mingw32/lib/libSDL2.dll.a", "libs/libSDL2.dll.a")
    rmtree("SDL2-2.24.0")

    with open("src/Main.cpp", "x") as f:
        f.write(
"""#define SDL_MAIN_HANDLED
#include <SDL2/SDL.h>
#include <SDL2/SDL_main.h>
#include <iostream>

#define WIDTH 800
#define HEIGHT 600
#define DELAY 3000

int main(int argc, char **argv) {
    SDL_Window *window = NULL;

    if (SDL_Init(SDL_INIT_VIDEO) != 0) {
        std::cerr << "SDL failed to initialise: " << SDL_GetError() << std::endl;
        return 1;
    }

    window = SDL_CreateWindow("SDL Example", SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, WIDTH, HEIGHT, 0);

    if (window == NULL) {
        std::cerr << "SDL window failed to initialise: " << SDL_GetError() << std::endl;
        return 1;
    }

    SDL_Renderer* renderer = NULL;
    renderer =  SDL_CreateRenderer(window, -1, SDL_RENDERER_ACCELERATED);

    SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);

    SDL_RenderClear(renderer);

    SDL_Rect r;
    r.x = 50;
    r.y = 50;
    r.w = 50;
    r.h = 50;

    SDL_SetRenderDrawColor(renderer, 255, 255, 255, 255);

    SDL_RenderFillRect(renderer, &r);

    SDL_RenderPresent(renderer);

    bool quit = false;

    while (!quit) {
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) quit = true;
        }
    }

    SDL_DestroyWindow(window);

    SDL_Quit(); 

    return 0;
}""")
    print("Created file 'Main.cpp'")


def compileProject():
    libs = ""
    for lib in listdir("libs"):
        if lib.endswith(".a"):
            libs += f"-l{lib[3:-2]} "
    system(f"g++ src/Main.cpp -o build/Game -Iinclude -Llibs -lSDL2 {libs}")


def runProject():
    system("build\Game.exe")


if __name__ == "__main__":
    if len(argv) == 2:
        action = argv[1]
        if action == "create":
            createProject()
        elif action == "build":
            compileProject()
        elif action == "run":
            runProject()
        else:
            print("This action does not exist")
    else:
        print("SDL-Project    Simple tool for working with SDL2 in C++")
        print("Arguments:")
        print("    create     Creates a project folder structure and downloads necessary SDL2 files")
        print("    build      Builds an executable")
        print("    run        Runs the program")
