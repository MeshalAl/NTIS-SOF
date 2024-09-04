from pydantic import BaseModel


class SOFUser(BaseModel):
    user_id: int
    account_id: int
    display_name: str
    user_age: int | None = None
    reputation: int
    location: str | None = None
    user_type: str
    last_access_date: int | None = None
    view_count: int | None = None
    question_count: int | None = None
    answer_count: int | None = None
    profile_image: str | None = None

    @staticmethod
    def _null_marker(val: str | int | None) -> str:
        if val:
            return str(val)
        else:
            return "__NULL__"

    @staticmethod
    def _null_de_marker(val: str) -> str | int | None:
        if val != "__NULL__":
            return int(val) if val.isdigit() else val
        else:
            return None

    def to_sofuser_string(self) -> str:
        return (
            "\t".join(
                map(
                    self._null_marker,
                    [
                        self.user_id,
                        self.account_id,
                        self.display_name,
                        self.user_age,
                        self.reputation,
                        self.location,
                        self.user_type,
                        self.last_access_date,
                        self.view_count,
                        self.question_count,
                        self.answer_count,
                        self.profile_image,
                    ],
                )
            )
            + "\n"
        )

    @classmethod
    def from_sofuser_string(cls, sofuser_string: str) -> "SOFUser":
        model_keys = list(cls.model_fields.keys())

        string_data = sofuser_string.strip().split("\t")

        demarked_sof_user_data = map(cls._null_de_marker, string_data)

        sof_user_data = dict(zip(model_keys, demarked_sof_user_data))
        return cls(**sof_user_data)  # type: ignore
