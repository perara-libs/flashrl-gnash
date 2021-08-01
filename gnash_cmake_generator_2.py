import glob
import argparse
import os
import pathlib

current_dir = pathlib.Path(__file__).parent.absolute()


def get_files(path, extensions):
    files_grabbed = [glob.glob(str(pathlib.Path(path).joinpath(e))) for e in extensions]
    flat_list = [item.replace(path + "/", "") for sublist in files_grabbed for item in sublist]
    return flat_list


def dotify(child_path: pathlib.Path, parent_path: pathlib.Path):
    dots = "../../"
    while child_path.absolute() != parent_path.absolute():
        dots += "../"
        child_path = child_path.parent
    return dots


if __name__ == "__main__":
    # libname

    template = '''cmake_minimum_required(VERSION 3.19)
project({libname})

{defines}

set({libname}_SOURCES 
{sources}
)

set({libname}_INCLUDE_DIRS 
.
{include_dirs}
)

set({libname}_LINK_TARGETS 
{links}
)



add_library({libname} STATIC ${{{libname}_SOURCES}})
target_link_libraries({libname} PUBLIC ${{{libname}_LINK_TARGETS}})
target_include_directories({libname} PUBLIC ${{{libname}_INCLUDE_DIRS}})


        '''

    parser = argparse.ArgumentParser()
    # parser.add_argument("--name", type=str, required=True)
    # parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()

    # full_path = args.path

    interface_path = current_dir.joinpath("interface2")
    src_path = current_dir.joinpath("gnash")
    project_registry = {}

    ignore = [
        "mysql",
        "cmake",
        "testsuite",
        "gtk", # TODO remove?
        "mkit",
        "sdl",  #TODO
        "aos4",
        "directfb", # TODO - smart_ptr.h
        "egl", # TODO
        "vaapi",
        "lirc",
        "x11",  # TODO
        "egl",
        "openvg",
        "opengles1",
        "agg",
        "aqua",
        "fltk",
        "qt",
        "dump",
        "haiku",
        "gst",
        "pythonmod",
        "cgi-bin",
        "npapi",
        "klash",
        "win32"
    ]

    ignore_sources = [
        "testr_gtk.cpp",
        "TouchDevice.cpp",
        "SharedMemW32.cpp",
        "GnashVaapiImage.cpp",
        "GnashVaapiTexture.cpp",
        "UinputDevice.cpp", # todo
        "testr.cpp",
        "fb_glue_agg.cpp",
        "GlibDeprecated.h",
        "findwebcams.cpp",
        "rtmp_server.cpp",
        "rtmp.cpp",
        "http_server.cpp",
        "fb_glue_ovg.cpp",
        "sslclient.cpp",
        "sslserver.cpp",
        "findmicrophones.cpp",
        "cvm.cpp",
        "dumpshm.cpp"
    ]

    links = [
        "uinput",
        "png_static",
        "${GIF_LIBRARIES}",
        "Boost",
        "OpenSSL::SSL OpenSSL::Crypto"

    ]

    defines = [
        "HAVE_LINUX_UINPUT_H=1",
        "ENABLE_SHARED_MEM=1",
        "HAVE_SHMGET",
        "HAVE_DIRENT_H=1",
        "GIFLIB_MAJOR=5",
        "GIFLIB_MINOR=1",
        "HAVE_SYSCONF=1",
        "HAVE_OPENSSL_SSL_H=1"
    ]

    all_sources = []
    all_include_dirs = []
    for root, subdirs, files in os.walk(src_path.relative_to(current_dir)):

        exit_out = False
        for i in ignore:
            if i in root:

                exit_out = True

        if exit_out:
            continue

        if root == str(src_path):
            continue

        sources = get_files(root, ["*.cpp", "*.h"])
        if len(sources) == 0:
            continue

        sources = [x for x in sources if x not in ignore_sources]



        all_sources.extend([f"../{root}/{x}" for x in sources])
        all_include_dirs.extend([f"../{root}"])



    cmake_target = "gnash_biglib"
    cmake_sources_str = '\n'.join(all_sources)
    cmake_include_dirs = '\n'.join(all_include_dirs)
    cmake_links = '\n'.join(links)
    cmake_defines = '\n'.join(["add_compile_definitions(" + x + ")" for x in defines])

    cmake_template = template.format(
        libname=cmake_target,
        sources=cmake_sources_str,
        include_dirs=cmake_include_dirs,
        links=cmake_links,
        defines=cmake_defines
    )
    interface_path.mkdir(exist_ok=True)
    cmake_project_file = interface_path.joinpath("CMakeLists.txt")
    with open(cmake_project_file, "w") as f:
        f.write(cmake_template)

    # Revno file
    headers_revno_h = interface_path.joinpath("revno.h")
    with headers_revno_h.open("w") as f:
        f.write("")

    # Revno file
    headers_revno_h = interface_path.joinpath("gnashconfig.h")
    with headers_revno_h.open("w") as f:
        f.write("")

    # debugger file
    headers_revno_h = interface_path.joinpath("debugger.h")
    with headers_revno_h.open("w") as f:
        f.write("")

