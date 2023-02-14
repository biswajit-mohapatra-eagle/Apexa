"""7-Zip Scraper."""

from apexa.common._typings import DATAFRAME
from apexa.common.model import Scraper
from apexa.common.util import (
    list_of_dict_to_pandas_df,
    re_search,
    web_driver_find_elements,
)


class SevenZipScraper(Scraper):
    """7-Zip Scraper."""

    url = "https://www.7-zip.org/history.txt"
    name = "7-ZIP"
    extra_date_fields = ["releaseDate"]

    def __init__(self, uuid):
        self.uuid = uuid
        super().__init__()

    def extract_version(self, text: str) -> str:
        """Extract the version from the text.

        :param text: the text to extract version from
        :returns extratced version
        """
        match = re_search(r"(([.]*\d+)*)", text)
        return match[1] + ".x"

    def start(self) -> DATAFRAME:
        """Get EOL data from txt file.

        :returns EOL data as dataframe
        """
        body = web_driver_find_elements(self.driver, "body", is_list=False)
        txt = body.text
        lines = txt.split("\n")

        # Select lines that have length and start with a digit
        wanted_lines = [line for line in lines if len(line) and line[0].isdigit()]
        list_of_rows = []
        for line in wanted_lines:
            new_row = {}

            # everything before the first 10 digits is the version,
            # strip any blank spaces
            new_row["originalVersion"] = line[:-10].lstrip().rstrip()

            # last ten digits are the release dates
            new_row["releaseDate"] = line[-10:]
            list_of_rows.append(new_row)

        data = list_of_dict_to_pandas_df(list_of_rows)
        data["originalEOLDate"] = data["releaseDate"]
        data["originalEOLDate"] = data["originalEOLDate"].shift(1)
        data["originalName"] = "7-Zip"
        data["originalEolSource"] = self.url

        # Cleaning up the versions and adding .x
        data["originalVersion"] = data["originalVersion"].apply(self.extract_version)

        # Dropping all "duplicates" picking the latest entry of a version
        data.drop_duplicates(
            ["originalName", "originalVersion"], keep="first", inplace=True
        )

        return data

    def eol_data_generator(self):
        """Collect EOL data into a dataframe, convert to json.

        :returns type: list[dict]
        """
        self.goto_url(self.url)
        eol_data_df = self.start()
        return eol_data_df
