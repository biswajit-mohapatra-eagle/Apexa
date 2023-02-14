"""IDERA Scraper."""

from apexa.common._typings import DATAFRAME
from apexa.common.model import Scraper
from apexa.common.util import (
    convert_table_to_pandas_dataframe,
    format_date,
    pandas_concat,
    re_search,
    web_driver_find_elements,
)


class IDERAScraper(Scraper):
    """IDERA Scraper."""

    url = "https://www.idera.com/support/sql-tools-supported-versions/"
    name = "IDERA"
    mapping = {
        "VERSION": "originalVersion",
        "LIMITED SUPPORT": "originalEOLDate",
        "END OF LIFE": "originalExtendedEOLDate",
        "announcement_url": "originalEolSource",
    }
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
        return f"{match[1]}.x"

    def fix_date_formats(self, dataframe: DATAFRAME) -> DATAFRAME:
        """Fix date formats in dataframe.

        :param dataframe
        :return dataframe
        """
        dataframe["RELEASE DATE"] = dataframe.apply(
            lambda row: format_date(row["RELEASE DATE"]),
            axis=1,
        )
        dataframe["LIMITED SUPPORT"] = dataframe.apply(
            lambda row: format_date(row["LIMITED SUPPORT"]),
            axis=1,
        )
        dataframe["END OF LIFE"] = dataframe.apply(
            lambda row: format_date(row["END OF LIFE"]),
            axis=1,
        )
        return dataframe

    def eol_data_generator(self) -> list[dict]:
        """Collect EOL data into a dataframe, convert to json.

        :returns type: list[dict]
        """
        # Go to the website
        self.goto_url(self.url, 5)

        # Find all software names
        software_names = web_driver_find_elements(
            self.driver, "h2", {"class": "supportDivTitle"}
        )

        # Find all tables
        tables = web_driver_find_elements(self.driver, "table")

        tables_as_df = convert_table_to_pandas_dataframe(tables)

        list_of_dataframes = []

        for software_name, dataframe in zip(software_names, tables_as_df):
            dataframe["originalName"] = software_name.text
            dataframe["originalEolSource"] = self.url
            dataframe.replace("\xa0", "", inplace=True)
            dataframe = self.fix_date_formats(dataframe)
            list_of_dataframes.append(dataframe)

        eol_data_df = pandas_concat(list_of_dataframes)

        eol_data_df["VERSION"] = eol_data_df["VERSION"].apply(self.extract_version)
        eol_data_df.drop_duplicates(
            ["originalName", "VERSION"], keep="first", inplace=True
        )

        return eol_data_df
