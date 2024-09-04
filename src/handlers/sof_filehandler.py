from pathlib import Path
from models.sof_models import SOFUser


class SOFFileHandler:

    _EXTENSION = ".sofusers"
    _DEFAULT_DATA_FOLDER = "data"

    def __init__(self, file_path: str) -> None:

        self.handler_path = Path(__file__).parent
        self.src_path = self.handler_path.parent
        self.root_path = self.src_path.parent
        self.data_folder = self.root_path / self._DEFAULT_DATA_FOLDER

        self.file_path = self._process_file_path(file_path, self.data_folder)

    def _process_file_path(self, file_path: str, default_data_folder) -> Path:
        path = Path(file_path)

        if path.is_absolute():
            return self._check_extention(path)

        return self._check_extention(Path(default_data_folder) / path)

    def _check_extention(self, file_path: Path) -> Path:
        if file_path.suffix != self._EXTENSION:
            return file_path.with_suffix(self._EXTENSION)
        return file_path

    def save(self, data: dict, overwrite: bool = False) -> None:
        # check if file exist, add to it, if not create new
        # format to sofusers file and save

        if self.file_path.exists() and not overwrite:
            # change total count and page count, append data to bottom of file.
            with open(self.file_path, "r+") as sof_file:
                pass
                # current_data = sof_file.read()
                # sof_file.write(str(data))

        with open(self.file_path, "w") as sof_file:
            sof_file.write(str(data))

    def load(self) -> dict:
        with open(self.file_path, "r") as sof_file:
            pass
        #     data = sof_file.read()
        # return data

    def _parse_user(self, data: str) -> dict:
        pass

    def _format_user(self, data: dict) -> str:
        pass


# WIP: new approach through SOFUSers to serialize and deserialize data
