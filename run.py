import shutil
import os
import sys
import re
from pathlib import Path
from time import sleep


DIR_SUFF_DICT = {
    "images": [
        '.jpg', '.jpeg', '.png', '.gif', '.tiff', '.ico', '.bmp', '.webp', '.svg'
    ],

    "documents": [
        ".pdf", ".md", ".epub", ".txt", ".docx", ".doc", ".ods", ".odt", ".dotx", ".docm", ".dox",
        ".rvg", ".rtf", ".rtfd", ".wpd", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".xml",
        ".html", ".htm", ".xhtml", ".py", ".pyw", ".pyc"
    ],

    "archives": [
        ".iso", ".tar", ".gz", ".7z", ".dmg", ".rar", ".zip"
    ],

    "audio": [
        ".aac", ".m4a", ".mp3", "ogg", ".raw", ".wav", ".wma", ".amr"
    ],

    "video": [
        ".avi", ".flv", ".wmv", ".mov", ".mp4", ".webm", ".vob", ".mpg", ".mpeg", ".3gp", ".mkv"
    ],
}

TRANS = {
    1072: 'a', 1040: 'A', 1073: 'b', 1041: 'B', 1074: 'v', 1042: 'V', 1075: 'g', 1043: 'G', 1076: 'd', 
    1044: 'D', 1077: 'e', 1045: 'E', 1105: 'e', 1025: 'E', 1078: 'j', 1046: 'J', 1079: 'z', 1047: 'Z', 
    1080: 'i', 1048: 'I', 1081: 'j', 1049: 'J', 1082: 'k', 1050: 'K', 1083: 'l', 1051: 'L', 1084: 'm', 
    1052: 'M', 1085: 'n', 1053: 'N', 1086: 'o', 1054: 'O', 1087: 'p', 1055: 'P', 1088: 'r', 1056: 'R', 
    1089: 's', 1057: 'S', 1090: 't', 1058: 'T', 1091: 'u', 1059: 'U', 1092: 'f', 1060: 'F', 1093: 'h', 
    1061: 'H', 1094: 'ts', 1062: 'TS', 1095: 'ch', 1063: 'CH', 1096: 'sh', 1064: 'SH', 1097: 'sch', 1065: 'SCH', 
    1098: '', 1066: '', 1099: 'y', 1067: 'Y', 1100: '', 1068: '', 1101: 'e', 1069: 'E', 1102: 'yu', 1070: 'YU', 
    1103: 'ya', 1071: 'YA', 1108: 'je', 1028: 'JE', 1110: 'i', 1030: 'I', 1111: 'ji', 1031: 'JI', 1169: 'g', 1168: 'G'
}

def sort(path: Path) -> dict:

    all_files = {
        "images": [],
        "documents": [],
        "archives": [],
        "audio": [],
        "video": [],
        "unknown": []
    }

    file_extensions = {}

    other_file_extensions = [0, set()]
    
    for el in path.iterdir():
        
        if el.is_file():

            for folder_name, suffixes in DIR_SUFF_DICT.items():
                if el.suffix.lower() in suffixes:

                    all_files[folder_name].append(el.name)

                    file_extensions[el.suffix] = (file_extensions[el.suffix]+1) if file_extensions.get(el.suffix) else 1

                    folder = path.joinpath(folder_name)

                    folder.mkdir(exist_ok=True)

                    file = el.rename(
                            f"{folder}/{normalize(el.name.removesuffix(el.suffix))}{el.suffix}"
                        )

                    if folder_name == "archives":
                        archive_folder = folder.joinpath(file.name.removesuffix(file.suffix))
                        archive_folder.mkdir(exist_ok=True)

                        shutil.unpack_archive(
                            file, 
                            archive_folder
                        )
                    
                    break
            else:
                all_files['unknown'].append(el.name)

                other_file_extensions[0] += 1
                other_file_extensions[1].add(el.suffix)

                el.rename(
                    f"{path}/{normalize(el.name.removesuffix(el.suffix))}{el.suffix}"
                )
        else:
            if not os.listdir(el):
                el.rmdir()

            elif el.name not in DIR_SUFF_DICT.keys():
                all_files_dir = sort(
                        el.rename(
                            f"{str(el.absolute()).removesuffix(el.name)}{normalize(el.name)}"
                        )
                    )
                for key, val in all_files_dir.items():
                    all_files[key].extend(val)
                

    print(f"\nУ каталозі «{path}» знайдено файли з розширенням:")
    print("{:^15}|{:>5}".format("Розширення", "Кількість"))

    for extension, quantity in file_extensions.items():
        print("{:^15}|{:>5}".format(extension, quantity))

    if other_file_extensions[0]:
        print(f"{other_file_extensions[0]} файлів з невідомими розширенням: {', '.join(other_file_extensions[1])}\n")

    return all_files

def normalize(name: str) -> str:
    return re.sub(r'([^\w\s]+)', lambda match: '_' * len(match.group()), name).translate(TRANS)

async def smart_split(text: str, chars_per_string: int=4096) -> list:

    async def _text_before_last(substr: str) -> str:
        return substr.join(part.split(substr)[:-1]) + substr

    if chars_per_string > 4096: chars_per_string = 4096

    parts = []
    while True:
        if len(text) < chars_per_string:
            parts.append(text)
            return parts

        part = text[:chars_per_string]

        if "\n" in part: part = _text_before_last("\n")
        elif ". " in part: part = _text_before_last(". ")
        elif " " in part: part = _text_before_last(" ")

        parts.append(part)
        text = text[len(part):]

def main():
    if len(sys.argv) < 2:
        raise Exception("[-] Аргументом при запуску скрипта не передано шлях до директорії")
    
    path = Path(sys.argv[1])

    if not path.exists():
        raise Exception("[-] Неіснуюча директорія")

    extensions = []

    for x in DIR_SUFF_DICT.values():
        extensions.extend(x)
        
    print(f"Пошук файлів з наступними розширеннями: {extensions}")

    sleep(5)

    file_extensions = sort(path)

    path.rename(
                f"{str(path.absolute()).removesuffix(path.name)}/SORTED"
            )
    
    print("\n[!] Сортування завершено\n")

    print("""
    Знайдено {images_len} файлів категорії images: {images}
    Знайдено {documents_len} файлів категорії documents: {documents}
    Знайдено {audio_len} файлів категорії audio: {audio}
    Знайдено {video_len} файлів категорії video: {video}
    Знайдено та розпаковано {archives_len} файлів категорії archives: {archives}
    Знайдено {archives_len} файлів з невідомим розширенням: {archives}
    """.format(
        images_len=len(file_extensions['images']), 
        documents_len=len(file_extensions['documents']), 
        audio_len=len(file_extensions['audio']), 
        video_len=len(file_extensions['video']), 
        archives_len=len(file_extensions['archives']), 
        unknown_len=len(file_extensions['unknown']), 
        **file_extensions
    ))

    sleep(15)
    

if __name__ == '__main__':
    main()
