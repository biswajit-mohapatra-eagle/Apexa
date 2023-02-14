"""Gurobi Scraper."""

from apexa.common._typings import DATAFRAME
from apexa.common.model import Scraper
from apexa.common.util import (
    convert_table_to_pandas_dataframe,
    pandas_concat,
    parse_date,
    web_driver_find_elements,
)


class GurobiScraper(Scraper):
    """Gurobi Scraper."""

    url = "https://support.gurobi.com/hc/en-us/articles/360048138771-Gurobi-release-and-support-history"  # pylint: disable=C0301
    name = "GUROBI"
    mapping = {"Version": "originalVersion", "Support ended": "originalEOLDate"}
    extra_date_fields = ["Released"]
    scraping_restricted = True

    def __init__(self, uuid):
        self.uuid = uuid
        super().__init__()

    def extract_version(self, text: str) -> str:
        """Extract the version from the text.

        :param text: the text to extract version from
        :returns extratced version
        """
        return f"{text}.x"

    def fix_date_formats(self, dataframe: DATAFRAME):
        """Fix date formats.

        :param dataframe: dataframe to fix date formats
        :returns dataframe with date formats fixed
        """
        dataframe["Released"] = dataframe.apply(
            lambda row: parse_date(row["Released"]), axis=1
        )
        dataframe["Support ended"] = dataframe.apply(
            lambda row: parse_date(row["Support ended"]), axis=1
        )

        return dataframe

    def eol_data_generator(self) -> list[dict]:
        """Collect EOL data into a dataframe, convert to json.

        :returns type: list[dict]
        """

        self.goto_url(self.url)

        tables = web_driver_find_elements(self.driver, "table")
        tables_as_df = convert_table_to_pandas_dataframe(tables)

        data = pandas_concat(tables_as_df)
        data = self.fix_date_formats(data)
        data["originalName"] = "Gurobi"
        data["originalEolSource"] = self.url
        data["Version"] = data["Version"].apply(self.extract_version)

        return data
