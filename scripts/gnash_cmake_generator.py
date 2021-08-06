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


set({libname}_SOURCES 
{sources}
)

set({libname}_INCLUDE_DIRS {include_dirs})

set({libname}_LINK_TARGETS 
{links}
)

{add_subdirs}

add_library({libname} {libtype} ${{{libname}_SOURCES}})
target_link_libraries({libname} {libtype_type} ${{{libname}_LINK_TARGETS}})
target_include_directories({libname} {libtype_type} ${{{libname}_INCLUDE_DIRS}})


        
        '''

    parser = argparse.ArgumentParser()
    # parser.add_argument("--name", type=str, required=True)
    # parser.add_argument("--path", type=str, required=True)
    args = parser.parse_args()

    # full_path = args.path

    interface_path = current_dir.joinpath("interface")
    src_path = current_dir.joinpath("gnash")
    project_registry = {}

    leaf_type = "INTERFACE"
    libtype_default = "INTERFACE"
    libtype_override = {
        "gui": "INTERFACE",
        "flash": "INTERFACE"
    }

    libtype_types = {
        "STATIC": "PUBLIC",
        "INTERFACE": "INTERFACE",
        "SHARED": "PUBLIC"
    }

    for root, subdirs, files in os.walk(src_path.relative_to(current_dir)):

        if "testsuite" in root:
            continue
        if "cmake" in root:
            continue
        if root == str(src_path):
            continue

        sources = get_files(root, ["*.cpp", "*.h"])

        if len(sources) == 0:
            continue

        cmake_project_name = root.replace("/", "_")
        cmake_project_path = interface_path.joinpath(root)

        code_subdirs = []
        for sd in subdirs:
            subdir_sources = get_files(str(pathlib.Path(root).joinpath(sd)), ["*.cpp", "*.h"])
            if len(subdir_sources) > 0:
                code_subdirs.append(sd)

        abs_path = pathlib.Path(current_dir).joinpath(root)
        relative_path = dotify(abs_path, src_path) + root


        # Determine library type
        cmake_libtype = libtype_default
        last_path = root.split("/")[-1]
        if last_path in libtype_override.keys():
            cmake_libtype = libtype_override[last_path]
        if len(subdirs) == 0:
            cmake_libtype = "INTERFACE"

        project_registry[cmake_project_name] = {
            "files": [relative_path + "/" + x for x in sources],
            "path": cmake_project_path,
            "subdirs": code_subdirs,
            "libtype": cmake_libtype,
            "include_dirs": relative_path
        }

    all_targets = set(project_registry.keys())
    for target in all_targets:
        cmake_project_link = all_targets - {target}
        cmake_project_link_str = '\n'.join(cmake_project_link)
        cmake_sources = project_registry[target]["files"]
        cmake_sources_str = '\n'.join(cmake_sources)
        cmake_project_path = project_registry[target]["path"]
        cmake_project_path.mkdir(parents=True, exist_ok=True)
        cmake_libtype = project_registry[target]["libtype"]
        cmake_include_dirs = project_registry[target]["include_dirs"]

        cmake_subproject = project_registry[target]["subdirs"]
        cmake_subproject_str = '\n'.join([f"add_subdirectory({x})" for x in cmake_subproject])

        cmake_template = template.format(
            libname=target,
            sources=cmake_sources_str,
            links=cmake_project_link_str,
            add_subdirs=cmake_subproject_str,
            libtype=cmake_libtype,
            libtype_type=libtype_types[cmake_libtype],
            include_dirs=cmake_include_dirs
        )
        cmake_project_file = cmake_project_path.joinpath("CMakeLists.txt")
        with open(cmake_project_file, "w") as f:
            f.write(cmake_template)
