premake.modules.sdl2 = {}
local m = premake.modules.sdl2

local p = premake

function progress(total, current)
    io.write("\r\x1b[2K")
    local ratio = current / total;
    ratio = math.min(math.max(ratio, 0), 1);
    local percent = math.floor(ratio * 100);
    io.write("Downloaded " .. math.floor((current / 1048576) * 10) / 10 .. "MB of " .. math.floor((total / 1048576) * 10) / 10 .. "MB " .. "(" .. percent .. "%/100%)")
end

newaction {
    trigger = "sdl2",
    description = "Download necessary files and generate project structure for SDL2 project",

    onStart = function()
        print("Starting SDL2 project generation")
    end,

    onWorkspace = function(wks)
    end,

    onProject = function(prj)
    end,

    execute = function()
        print("Downloading SDL2 zip archive")
        res = http.get("https://api.github.com/repos/libsdl-org/SDL/releases/latest")
        res = json.decode(res)
        for k, v in pairs(res["assets"]) do
            for k2, v2 in pairs(v) do
                if string.match(k2, "browser_download_url") and string.match(v2, "mingw.zip") then
                    zip_url = v2
                    break
                end
            end
        end
        term.pushColor(term.lightBlue)
        http.download(zip_url, "SDL2.zip", {progress = progress})
        term.pushColor(term.lightGray)

        print("\nExtracting SDL2 zip archive")
        zip.extract("SDL2.zip", "./")
        ok, err = os.remove("SDL2.zip")
        if not ok then
            error(err)
        end

        print("Generating project structure")
        os.mkdir("assets")
        os.mkdir("include")
        os.mkdir("libs")
        os.mkdir("src")
        f = io.open("src/Main.cpp", "w")
        f:write("// Main.cpp")
        f:close()

        os.copyfile("SDL2-2.24.0/x86_64-w64-mingw32/bin/SDL2.dll", "./SDL2.dll")
        os.execute("xcopy SDL2-2.24.0\\x86_64-w64-mingw32\\include\\SDL2\\* include\\SDL2\\* /I /Y > nul")
        os.copyfile("SDL2-2.24.0/x86_64-w64-mingw32/lib/libSDL2.dll.a", "libs/libSDL2.dll.a")
        
        os.execute("rmdir SDL2-2.24.0 /S /Q")
    end,

    onEnd = function()
        term.pushColor(term.lightGreen)
        print("SDL2 project generation complete")
        term.pushColor(term.lightGray)
    end
}

return m
