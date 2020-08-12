"""
The state module contains the State class and potential helper methods.
"""
from datetime import datetime
from typing import Optional


class State:
    """
    State controls the state file which is saving the last date and transaction
    hash.
    """

    filename: str
    start_date_config: Optional[datetime]

    def __init__(self, filename: str, start_date_config: Optional[datetime] = None):
        self.filename = filename
        self.start_date_config = start_date_config

    def restore(self) -> (datetime, str):
        """
        Restore returns the datetime and last hash. If no date could be found,
        it falls back to the provided fallback_date.
        """
        start_date: Optional[datetime] = None
        last_hash: Optional[str] = None
        try:
            with open(self.filename, "r") as state_file:
                contents = state_file.read().splitlines()
                start_date = datetime.fromisoformat(contents[0])
                last_hash = contents[1]
        except:  # pylint: disable=bare-except
            if self.start_date_config is not None:
                start_date = self.start_date_config
            else:
                start_date = datetime.now()

        return (start_date, last_hash)

    def store(self, last_hash: str) -> None:
        """
        Save the current date and last hash back to the file.
        """
        with open(self.filename, "w") as state_file:
            state_file.write(
                "%s\n%s" % (datetime.now().strftime("%Y-%m-%d"), last_hash,)
            )
