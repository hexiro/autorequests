import argparse
from pathlib import Path
from typing import List

from .classes import Class, File
from .utils import PathType


class AutoRequests(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()
        self.add_argument("-i", "--input", default=None, help="Input Directory")
        self.add_argument("-o", "--output", default=None, help="Output Directory")
        self.add_argument("--return-text", action="store_true",
                          help="Makes the generated method's responses return .text instead of .json()")
        self.add_argument("--single-quote", action="store_true", help="Uses single quotes instead of double quotes")
        self.add_argument("--no-headers", action="store_true", help="Removes all headers from the operation")
        self.add_argument("--no-cookies", action="store_true", help="Removes all cookies from the operation")
        args = self.parse_args()

        # resolves path
        self.__input = (Path(args.i) if args.input else Path.cwd()).resolve()
        self.__output = (Path(args.o) if args.output else Path.cwd()).resolve()
        self.__single_quote = args.single_quote
        self.__return_text = args.return_text
        self.__no_headers = args.no_headers
        self.__no_cookies = args.no_cookies

        # dynamic tings from here on out
        self.__classes = []
        self.__files = []
        self.__has_written = False

    @property
    def input(self) -> PathType:
        return self.__input

    @property
    def output(self) -> PathType:
        return self.__output

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

    # dynamic

    @property
    def classes(self) -> List[Class]:
        return self.__classes

    @property
    def files(self) -> List[File]:
        return self.__files

    @property
    def has_written(self):
        return self.__has_written

    def write(self):
        if self.has_written:
            return

        # handle local files
        self.parse_directory(self.input)

        output_folder = self.output.name

        # add non-local files and write python files
        for class_object in self.classes:
            class_name = class_object.name
            # create directories
            if class_name == output_folder:
                # ex. class is named "autorequests" and output folder is named "autorequests"
                class_folder = self.output
            else:
                class_folder = self.output / class_name
                # add methods from class folder
                if class_folder.exists():
                    self.parse_directory(class_folder)
                else:
                    class_folder.mkdir(parents=True)
            with (class_folder / "main.py").open(mode="w") as py:
                py.write(class_object.code())

        # move local files into class folder
        for file in self.files:
            class_name = file.method.class_name
            if output_folder != class_name:
                file.rename(self.output / class_name / file.name)
        self.__has_written = True

    def print_results(self):
        if len(self.classes) == 0:
            print("No request data could be located.")
            return
        if not self.has_written:
            print("Modules haven't been written to the filesystem yet.")
            return
        num_classes = len(self.classes)
        num_methods = len(self.files)
        classes_noun = "classes" if num_classes > 1 else "class"
        methods_noun = "methods" if num_methods > 1 else "method"
        print(f"Successfully wrote {num_classes} {classes_noun} with a total of {num_methods} {methods_noun}.")

    def parse_directory(self, directory: Path):
        if not directory.exists():
            return
        for file in directory.glob("*.txt"):
            file = File(file)
            method = file.method
            if method:
                class_name = file.method.class_name
                classes_search = [c for c in self.classes if c.name == class_name]

                if len(classes_search) == 0:
                    class_object = Class(name=class_name,
                                         return_text=self.return_text,
                                         single_quote=self.single_quote)
                    self.classes.append(class_object)
                else:
                    class_object = classes_search[0]

                # needs to be added first
                # modifying methods after adding it to the class is perfectly fine

                class_object.add_method(method)
                method.attach_class(class_object)
                self.files.append(file)

                # maybe this could be optimized?
                # cpu is wasted calculating headers and cookies only to be deleted
                if self.no_headers:
                    file.method.headers = {}
                if self.no_cookies:
                    file.method.cookies = {}


def main():
    auto_requests = AutoRequests()
    auto_requests.write()
    auto_requests.print_results()


if __name__ == "__main__":
    main()
