from datetime import datetime
from typing import Optional


class State:
    """
    State controls the state file which is saving the last date and transaction
    hash.
    """

    filename: str

    def __init__(self, filename: str):
        self.filename = filename

    def restore(self, fallback_date: Optional[datetime] = None) -> (datetime, str):
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
            start_date = fallback_date
        return (start_date, last_hash)

    def store(self, last_hash: str) -> None:
        """
        Save the current date and last hash back to the file.
        """
        with open(self.filename, "w") as state_file:
            state_file.write(
                "%s\n%s" % (datetime.now().strftime("%Y-%m-%d"), last_hash,)
            )
