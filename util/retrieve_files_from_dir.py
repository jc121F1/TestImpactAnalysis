import pathlib
import glob

def get_file_names_from_directory(list_of_directories):
    files = []
    for dir in list_of_directories:
        dir_path = pathlib.Path(dir)
        for file in dir_path.rglob("*"):
            files.append(file.absolute())

    return files
