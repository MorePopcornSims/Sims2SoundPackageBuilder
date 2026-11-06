import struct
import sys
from collections.abc import Iterable
from pathlib import Path
from tkinter import *
from tkinter import filedialog, messagebox, ttk

from crc import Calculator, Configuration

# App constants
SUPPORTED_EXTENSIONS = {".mp3", ".xa"}

# Resource identifiers
AUDIO_TYPE = 0x2026960B
AUDIO_GROUP = 0x0B8AB3CD
INITIALISER_GROUP = 0xADD550A7

# Package constants
HEADER_FORMAT = "<4s15I32s"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
INDEX_ENTRY_FORMAT = "<6I"
INDEX_ENTRY_SIZE = struct.calcsize(INDEX_ENTRY_FORMAT)

instance_high_calc = Calculator(
    Configuration(
        width=32,
        polynomial=0x04C11DB7,
        init_value=0xFFFFFFFF,
        final_xor_value=0x00000000,
        reverse_input=False,
        reverse_output=False,
    )
)

instance_low_calc = Calculator(
    Configuration(
        width=24,
        polynomial=0x01864CFB,
        init_value=0x00B704CE,
        final_xor_value=0xFF000000,
        reverse_input=False,
        reverse_output=False,
    )
)

def instance_high_hash(name: str) -> int:
    name = name.strip().lower().encode("utf-8")
    hash = instance_high_calc.checksum(name)
    return(hash)


def instance_low_hash(name: str) -> int:
    name = name.strip().lower().encode("utf-8")
    hash = instance_low_calc.checksum(name) 
    return(hash)


def get_folder():
    folder = filedialog.askdirectory(title="Select folder containing MP3/XA files", mustexist=TRUE)
    return(None if folder == "" else Path(folder))


def get_output_path():
    output_path = filedialog.asksaveasfilename(
                title="Save Sims 2 package",
                defaultextension=".package",
                filetypes=[("Sims 2 package", "*.package")],
            )
    return (Path(output_path))


def get_audio_files(folder: Path, recursive: bool = False) -> list[Path]:
    iterator: Iterable[Path] = folder.rglob("*") if recursive else folder.iterdir()
    
    audio_files = [p for p in iterator if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS]
    
    if not audio_files:
        raise ValueError("No .mp3 or .xa files were found in the selected folder.")
    return audio_files


def get_audio_initialiser() -> bytes:
    if getattr(sys, "frozen", False):
        # Running as a packaged PyInstaller application
        base_path = Path(sys._MEIPASS)
    else:
        # Running as a normal Python script
        base_path = Path(__file__).resolve().parent

    ini_path = base_path / "assets" / "audio.ini"

    if not ini_path.is_file():
        raise FileNotFoundError(
            f"Could not find audio initialiser:\n{ini_path}"
        )

    data = ini_path.read_bytes()

    return data


def create_resource_list(audio_files: list[Path], output_path: Path) -> list:    
    resources = []
    
    # Add the standard audio initialiser to the list.
    ini = {
            "type": AUDIO_TYPE,
            "group": INITIALISER_GROUP,
            "instance_high": instance_high_hash(output_path.stem),
            "instance_low": instance_low_hash(output_path.stem),
            "data": get_audio_initialiser()
        }
    resources.append(ini)

    # Add the data for each audio file to the list.
    for file in audio_files:
        resource = {
            "type": AUDIO_TYPE,
            "group": AUDIO_GROUP,
            "instance_low": instance_low_hash(file.stem),
            "instance_high": instance_high_hash(file.stem),
            "data": file.read_bytes()
        }

        resources.append(resource)
    
    return(resources)


def create_package(resources: list, output_path: Path):
    package_index = []
    package_data = []
    data_offset = HEADER_SIZE + (len(resources) * INDEX_ENTRY_SIZE)

    # Create the package index and data list.
    for resource in resources:
        package_index.append(
            struct.pack(
                INDEX_ENTRY_FORMAT,
                resource["type"],
                resource["group"],
                resource["instance_low"],
                resource["instance_high"],
                data_offset,
                len(resource["data"]),
            )
        )

        package_data.append(resource["data"])
        data_offset += len(resource["data"])

    package_index = b"".join(package_index)

    # Create the package header.
    package_header = struct.pack(
        HEADER_FORMAT,
        b"DBPF",
        1, 1,               # DBPF version
        0, 0, 0, 0, 0,      # Date and reserved fields
        7,                  # Index major version
        len(resources),     # Resource count
        HEADER_SIZE,        # Index offset
        len(package_index), # Index size
        0, 0, 0,            # Hole table fields
        2,                  # Index minor version
        bytes(32),          # Reserved bytes
    )

    # Save the package.
    while True:
        try:
            with output_path.open("wb") as package:
                package.write(package_header)
                package.write(package_index)

                for item in package_data:
                    package.write(item)

            messagebox.showinfo(title="Success", message="Package created!")
            return True

        except PermissionError:
            answer = messagebox.askyesno(title="Retry?", message="Could not write to file. It's probably open in SimPE. Do you want to try again?")
            if answer == NO:
                return False


class SoundPackageBuilder:

    def __init__(self, root):
        self.root = root
        self.root.title("Poppy's Sims 2 Sound Package Builder")
        self.folder = StringVar()
        self.recursive = BooleanVar()
        self.audio_files = []
        self.audio_files_var = StringVar(value=self.audio_files)
        self.status = StringVar(value="Select a folder of audio files.")

        self.build_ui()


    def build_ui(self):
        content = ttk.Frame(self.root, padding=(10))
        content.grid(column=0, row=0, sticky=(N, E, S, W))

        # Description
        ttk.Label(content, text="Combine a folder of .mp3 or .xa files into one Sims 2 package. The audio initialiser will be included automatically.").grid(row=1, column=1, columnspan=3, pady=(0,10), sticky=W) 

        # Folder Selection
        ttk.Label(content, text="Folder:", width=10).grid(row=2, column=1, sticky=E)

        folder_entry = ttk.Entry(content, width=100, textvariable=self.folder)
        folder_entry.grid(row=2, column=2, sticky=(W,E))

        ttk.Button(content, text="Select Folder", command=self.select_folder).grid(row=2, column=3, padx=5, sticky=E)

        ttk.Checkbutton(content, text="Include Subfolders", variable=self.recursive, command=self.refresh_file_list).grid(row=3, column=2, sticky=W)

        # File List
        file_list = Listbox(content, listvariable=self.audio_files_var, height=10)
        file_list.grid(row=4, column=1, columnspan=3, pady=10, sticky=(N, E, S, W))
        scroll = ttk.Scrollbar(content, orient=VERTICAL, command=file_list.yview)
        scroll.grid(row=4, column=4, sticky=(N, S))
        file_list.configure(yscrollcommand=scroll.set)

        # Status Bar
        ttk.Label(content, textvariable=self.status, padding=5, relief="sunken").grid(row=5, column=1, columnspan=2, sticky=(E, W, S))
        
        # Create Package Button
        self.save_button = ttk.Button(content, text="Save Package", command=self.save_package, state=DISABLED)
        self.save_button.grid(row=5, column=3, padx=5, sticky=E)

        content.columnconfigure(2, weight=3)
        content.rowconfigure(4, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)


    def select_folder(self):
        folder = get_folder()
        if not folder is None:
            self.folder.set(folder)
            self.refresh_file_list()


    def save_package(self):
        output_path = get_output_path()
        resources = create_resource_list(self.audio_files, output_path)
        result = create_package(resources, output_path)
        if result:
            self.status.set("Package saved!")
        else:
            self.status.set("Failed to save package.")


    def refresh_file_list(self):
        try:
            self.audio_files = get_audio_files(Path(self.folder.get()), self.recursive.get())
            self.audio_files_var.set(self.audio_files)
            self.status.set(f"{len(self.audio_files)} audio files found. Ready to create package.")
            self.save_button.state(['!disabled'])

        except ValueError as e:
            self.audio_files_var.set("")
            self.status.set(e)
            self.save_button.state(['disabled'])


def main():
    root = Tk()
    SoundPackageBuilder(root)
    root.mainloop()

    
if __name__ == "__main__":
    main()
