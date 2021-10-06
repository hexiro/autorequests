import argparse
from pathlib import Path
from typing import List

from . import __version__
from .classes import Class, InputFile, OutputFile


class AutoRequests:
    # filepath: Path
    # filename: str
    # file: File

    def __init__(self):
        super().__init__()
        parser = argparse.ArgumentParser()
        parser.add_argument("-i", "--input", default=None, help="Input Directory")
        parser.add_argument("-o", "--output", default=None, help="Output Directory")
        parser.add_argument("-v", "--version", action="store_true")
        parser.add_argument("--return-text",
                            action="store_true",
                            help="Makes the generated method's responses return .text instead of .json()"
                            )
        parser.add_argument("--single-quote", action="store_true", help="Uses single quotes instead of double quotes")
        parser.add_argument("--no-headers", action="store_true", help="Removes all headers from the operation")
        parser.add_argument("--no-cookies", action="store_true", help="Removes all cookies from the operation")
        parser.add_argument("--compare", action="store_true",
                            help="Compares the previously generated files to the new files."
                            )
        parser.add_argument("--parameters",
                            action="store_true",
                            help="Replaces hardcoded params, json, data, etc with parameters that have default values")
        args = parser.parse_args()

        # resolves path
        self.__input = (Path(args.i) if args.input else Path.cwd()).resolve()
        self.__output = (Path(args.o) if args.output else Path.cwd()).resolve()
        self.__version = args.version
        self.__single_quote = args.single_quote
        self.__return_text = args.return_text
        self.__no_headers = args.no_headers
        self.__no_cookies = args.no_cookies
        self.__compare = args.compare
        self.__parameters_mode = args.parameters

        # dynamic tings from here on out
        self.__classes = []
        self.__input_files = []
        self.__output_files = []
        self.__has_written = False

    @property
    def input(self) -> Path:
        return self.__input

    @property
    def output(self) -> Path:
        return self.__output

    @property
    def version(self) -> bool:
        return self.__version

    @property
    def single_quote(self) -> bool:
        return self.__single_quote

    @property
    def return_text(self) -> bool:
        return self.__return_text

    @property
    def no_headers(self) -> bool:
        return self.__no_headers

    @property
    def no_cookies(self) -> bool:
        return self.__no_cookies

    @property
    def compare(self) -> bool:
        return self.__compare

    @property
    def parameters_mode(self) -> bool:
        return self.__parameters_mode

    # dynamic

    @property
    def classes(self) -> List[Class]:
        return self.__classes

    @property
    def input_files(self) -> List[InputFile]:
        return self.__input_files

    @property
    def output_files(self) -> List[OutputFile]:
        return self.__output_files

    @property
    def has_written(self) -> bool:
        return self.__has_written

    def load_local_files(self):
        self.parse_directory(self.input)

    def main(self):
        if self.version:
            print(f"AutoRequests {__version__}")
            return
        self.load_local_files()
        self.load_external_files()
        self.write()
        self.move_into_class_folder()
        self.print_results()

    def load_external_files(self):
        for output_file in self.output_files:
            if not output_file.in_same_dir():
                if output_file.folder.is_dir():
                    self.parse_directory(output_file.folder)
                else:
                    output_file.folder.mkdir()

    def write(self):
        if self.has_written:
            return

        for output_file in self.output_files:
            # need to check changes before writing again
            if self.compare and output_file.python_file.is_file():
                output_file.write_changes()
            output_file.write()

        self.__has_written = True

    def move_into_class_folder(self):
        for file in self.input_files:
            class_name = file.method.class_name
            if self.output.name != class_name:
                file.rename(self.output / class_name / file.name)

    def print_results(self):
        if len(self.classes) == 0:
            print("No request data could be located.")
            return
        if not self.has_written:
            print("Modules haven't been written to the filesystem yet.")
            return
        num_classes = len(self.classes)
        num_methods = len(self.input_files)
        classes_noun = "classes" if num_classes > 1 else "class"
        methods_noun = "methods" if num_methods > 1 else "method"
        print(f"Successfully wrote {num_classes} {classes_noun} with a total of {num_methods} {methods_noun}.")

    def parse_directory(self, directory: Path):
        if not directory.is_dir():
            return
        for filename in directory.glob("*.txt"):
            file = InputFile(filename)
            method = file.method
            if method:
                class_name = file.method.class_name
                class_object = next((c for c in self.classes if c.name == class_name), None)
                if not class_object:
                    class_object = Class(name=class_name,
                                         return_text=self.return_text,
                                         single_quote=self.single_quote,
                                         parameters_mode=self.parameters_mode)
                    self.classes.append(class_object)
                    self.output_files.append(OutputFile(self.output, class_object))

                # needs to be added first

                class_object.add_method(method)
                self.input_files.append(file)

                # maybe this could be optimized?
                # cpu is wasted calculating headers and cookies only to be deleted
                if self.no_headers:
                    method.headers = {}
                if self.no_cookies:
                    method.cookies = {}


def main():
    AutoRequests().main()


if __name__ == "__main__":
    main()
