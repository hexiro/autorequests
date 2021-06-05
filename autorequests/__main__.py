import argparse
from pathlib import Path

from .classes import Class, File


class AutoRequests(argparse.ArgumentParser):

    def __init__(self):
        super().__init__()
        self.add_argument("-i", "--input", default=None, help="Input Directory")
        self.add_argument("-o", "--output", default=None, help="Output Directory")
        self.add_argument("--no-headers", action="store_true", help="Removes all headers from the operation")
        self.add_argument("--no-cookies", action="store_true", help="Removes all cookies from the operation")
        args = self.parse_args()

        # resolves path
        self.__input = (Path(args.i) if args.input else Path.cwd()).resolve()
        self.__output = (Path(args.o) if args.output else Path.cwd()).resolve()
        self.__no_headers = args.no_headers
        self.__no_cookies = args.no_cookies

        # dynamic tings from here on out
        # class_name: Class()
        self.__classes = {}
        # []File
        self.__files = []
        self.__has_written = False

    def write(self):
        if self.has_written:
            return

        # handle local files
        self.parse_directory(self.input)

        output_folder = self.output.name

        # add non-local files and write python files
        for class_name, class_object in self.__classes.items():
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
        for file in self.__files:
            class_name = file.method.class_name
            if output_folder != class_name:
                file.rename(self.output / class_name / file.name)
        self.__has_written = True

    def print_results(self):
        if len(self.classes) == 0:
            print("No fetches could be located.")
            return
        if not self.has_written:
            print("Modules haven't been written to the filesystem yet.")
            return
        num_classes = len(self.classes)
        num_methods = len(self.methods)
        classes_noun = "classes" if num_classes > 1 else "class"
        methods_noun = "methods" if num_methods > 1 else "method"
        print(f"Successfully wrote {num_classes} {classes_noun} with a total of {num_methods} {methods_noun}.")

    def parse_directory(self, directory: Path):
        if not directory.exists():
            return
        for file in directory.glob("*.txt"):
            file = File(file)
            if not file.method:
                return
            class_name = file.method.class_name
            if class_name not in self.__classes:
                self.__classes[class_name] = Class(class_name)

            # needs to be added first
            # modifying methods after adding it to the class is perfectly fine

            self.__classes[class_name].add_method(file.method)
            self.__files.append(file)

            # maybe this could be optimized?
            # cpu is wasted calculating headers and cookies only to be deleted
            if self.__no_headers:
                file.method.headers = {}
            if self.__no_cookies:
                file.method.cookies = {}

    @property
    def has_written(self):
        return self.__has_written

    # technically these both return WindowsPath or PosixPath
    # but I don't see specifying the more abstracted, 'Path' being an issue.

    @property
    def input(self) -> Path:
        return self.__input

    @property
    def output(self) -> Path:
        return self.__output

    @property
    def classes(self) -> dict:
        return self.__classes

    @property
    def methods(self) -> list:
        return self.__files


def main():
    auto_requests = AutoRequests()
    auto_requests.write()
    auto_requests.print_results()


if __name__ == "__main__":
    main()
