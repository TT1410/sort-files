import shutil
import os
import sys
import re
from pathlib import Path
from time import sleep
from constants import DIR_SUFF_DICT, TRANS, FOUND_FILES


def sort(path: Path) -> None:
    file_extensions = {}
    other_file_extensions = [0, set()]
    
    for el in path.iterdir():
        
        if el.is_file():
            folder_name = file_moderation(el, path)

            if folder_name:
                file_extensions[el.suffix] = (file_extensions[el.suffix]+1) if file_extensions.get(el.suffix) else 1
                
            else:
                other_file_extensions[0] += 1
                other_file_extensions[1].add(el.suffix)

        else:
            folder_moderation(el)
    
    report_folder(path, file_extensions, other_file_extensions)


def file_moderation(file: Path, path: Path) -> str|None:

    for folder_name, suffixes in DIR_SUFF_DICT.items():
        if file.suffix.lower() in suffixes:

            FOUND_FILES[folder_name].append(file.name)

            folder = path.joinpath(folder_name)

            folder.mkdir(exist_ok=True)

            file = file.rename(
                    f"{folder.joinpath(normalize(file.name.removesuffix(file.suffix)))}{file.suffix}"
                )

            if folder_name == "archives":
                archive_folder = folder.joinpath(file.name.removesuffix(file.suffix))
                archive_folder.mkdir(exist_ok=True)

                try:
                    shutil.unpack_archive(
                        file, 
                        archive_folder
                    )
                except shutil.ReadError as e:
                    print(f"Виникла помилка: {e}\nНевдала спроба розпакувати архів: {file.absolute()}")
            
            return folder_name
    
    else:
        FOUND_FILES["unknown"].append(file.name)

        file.rename(
            f"{path.joinpath(normalize(file.name.removesuffix(file.suffix)))}{file.suffix}"
        )


def folder_moderation(folder: Path) -> None:
    if not os.listdir(folder):
        folder.rmdir()

    elif folder.name not in DIR_SUFF_DICT.keys():
        sort(
            folder.rename(
                f"{str(folder.absolute()).removesuffix(folder.name)}{normalize(folder.name)}"
            )
        )


def normalize(name: str) -> str:
    return re.sub(r'([^\w\s]+)', lambda match: '_' * len(match.group()), name).translate(TRANS)


def report_folder(path: Path, file_extensions: dict, other_file_extensions: list) -> dict[str, list]:

    print(f"\nУ каталозі «{path}» знайдено файли з розширенням:")
    print("{:^15}|{:>5}".format("Розширення", "Кількість"))

    for extension, quantity in file_extensions.items():
        print("{:^15}|{:>5}".format(extension, quantity))

    if other_file_extensions[0]:
        print(f"{other_file_extensions[0]} файлів з невідомим розширенням: {', '.join(other_file_extensions[1])}\n")


def main() -> None:
    if len(sys.argv) < 2:
        raise Exception("[-] Аргументом при запуску скрипта не передано шлях до директорії")
    
    root_folder = Path(sys.argv[1])

    if not root_folder.exists():
        raise Exception("[-] Неіснуюча директорія")

    elif root_folder.is_file():
        raise Exception("[-] За даним шляхом знаходиться файл")

    extensions = []

    for ext in DIR_SUFF_DICT.values():
        extensions.extend(ext)
        
    print(f"Пошук файлів з наступними розширеннями: {extensions}")
    sleep(5)

    sort(root_folder)

    root_folder.rename(
        Path(str(root_folder.absolute()).removesuffix(root_folder.name))
        .joinpath("SORTED")
    )
    
    print("""\n[!] Сортування завершено
    Знайдено {images_len} файлів категорії images: {images}
    Знайдено {documents_len} файлів категорії documents: {documents}
    Знайдено {audio_len} файлів категорії audio: {audio}
    Знайдено {video_len} файлів категорії video: {video}
    Знайдено та розпаковано {archives_len} файлів категорії archives: {archives}
    Знайдено {unknown_len} файлів з невідомим розширенням: {unknown}
    """.format(
        images_len=len(FOUND_FILES['images']), 
        documents_len=len(FOUND_FILES['documents']), 
        audio_len=len(FOUND_FILES['audio']), 
        video_len=len(FOUND_FILES['video']), 
        archives_len=len(FOUND_FILES['archives']), 
        unknown_len=len(FOUND_FILES['unknown']), 
        **FOUND_FILES
    ))


if __name__ == '__main__':
    main()
