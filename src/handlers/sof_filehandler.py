from pathlib import Path
from models.sof_models import SOFUser, SOFFile
from config.config_loader import Config
from typing import List
from handlers.utility import get_epoch_time


class SOFFileHandler:

    _EXTENSION = ".sofusers"
    _MODES = ("w", "r")
    _MARKER = "SOFFILE"
    _PATTERN = "user_data_*.sofusers"

    def __init__(self, config: Config) -> None:

        self.handler_path = Path(__file__).parent
        self.src_path = self.handler_path.parent
        self.root_path = self.src_path.parent
        self.default_data_folder = self.root_path / config.sof_handler.default_path

    def save(
        self,
        sof_users: list[SOFUser],
        meta: dict,
        sof_path: str | None = None,
        mode: str = "w",
    ) -> None:
        # multiple mode support?, maybe later.

        if not sof_users:
            raise ValueError("No users to save")

        if mode not in self._MODES:
            raise ValueError(f"Invalid mode: {mode}")

        self.resolved_path = self._resolve_path(sof_path, mode)
        # saved to instance so i can resuse whenever i need to save again.

        if not self.resolved_path.exists():
            self.resolved_path.touch()

        total_users_fetched = len(sof_users)
        total_pages = meta.get("total_pages", 1)

        sof_header = self._get_sofheader(total_users_fetched, total_pages)
        sofuser_strings = self._format_users(sof_users)

        try:
            with open(self.resolved_path, mode) as sof_file:
                sof_file.write(sof_header)
                sof_file.write("\n")
                sof_file.writelines(sofuser_strings)
        except Exception as e:
            raise e

    def load(self, file_path: str | None = None, mode: str = "r") -> SOFFile:

        resolved_path = self._resolve_path(file_path, mode=mode)
        if not resolved_path.exists():
            raise FileNotFoundError(f"file not found: {resolved_path}")

        try:
            with open(resolved_path, "r") as sof_file:
                marker, header = sof_file.readline().split("%")
                total_users_fetched, total_pages = header.split("\t")

                if marker != self._MARKER:
                    raise ValueError("invalid file format or bad header")

                total_users_fetched, total_pages = header.split("\t")
                serialized_users = sof_file.readlines()
                sof_users = self._parse_users(serialized_users)
            return SOFFile(
                users=sof_users,
                meta={
                    "total_users_fetched": int(total_users_fetched),
                    "total_pages": int(total_pages),
                    "file_path": str(resolved_path),
                },
            )
        except Exception as e:
            raise e

    def _resolve_path(self, unresolved_path: str | None, mode: str) -> Path:

        if not unresolved_path:
            match mode:
                case "w":
                    return self.default_data_folder / self._generate_filename()
                case "r":
                    return self._get_latest_default_file(pattern=self._PATTERN)

        file_path = Path(unresolved_path)

        if file_path.is_absolute():
            if not file_path.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.touch()

            return self._check_extention(file_path)

        return self._check_extention(self.default_data_folder / file_path)

    def _check_extention(self, file_path: Path) -> Path:

        if file_path.suffix:
            if file_path.suffix != self._EXTENSION:
                raise ValueError(f"file not a valid .sofusers: {file_path}")
            return file_path
        return self._add_suffix(file_path)

    def _add_suffix(self, file_path: Path) -> Path:
        # after we check if the path is valid, we add the suffix to the given name
        return file_path.with_suffix(self._EXTENSION)

    def _parse_users(self, serialized_strings: List[str]) -> List[SOFUser]:
        sof_users = []
        for sofuser_string in serialized_strings:

            if sofuser_string == "\n":
                continue
            try:
                sof_user = SOFUser.deserialize_sofuser(sofuser_string)
            except Exception as e:
                raise e
            sof_users.append(sof_user)
        return sof_users

    def _format_users(self, data: List[SOFUser]) -> List[str]:
        if not data:
            raise ValueError("no valid users to format")

        formatted_users = [user.serialize_sofuser() for user in data]
        return formatted_users

    def _get_latest_default_file(self, pattern: str) -> Path:
        files = self.default_data_folder.glob(pattern)
        if not files:
            raise FileNotFoundError("No files found in default data folder")

        latest_file = max(files, key=self._get_file_birthtime)
        return latest_file

    @staticmethod
    def _get_file_birthtime(file: Path) -> float:
        return file.stat().st_birthtime

    @staticmethod
    def _generate_filename() -> str:
        return f"user_data_{get_epoch_time()}.sofusers"

    def _get_sofheader(self, total_users_fetched: int, total_pages: int) -> str:
        marker = "SOFFILE%"
        header = f"{marker}{total_users_fetched}\t{total_pages}\n"
        return header

