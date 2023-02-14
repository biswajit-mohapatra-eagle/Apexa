"""TomiTribe Scraper."""

from apexa.common._typings import DATAFRAME
from apexa.common.model import Scraper
from apexa.common.util import (
    convert_table_to_pandas_dataframe,
    drop_multilevel_index,
    format_date,
    pandas_concat,
    web_driver_find_elements,
)


class TomitribeScraper(Scraper):
    """Tomitribe Scraper."""

    url = "https://www.tomitribe.com/legal/lifecycle-policy/"
    name = "TOMITRIBE"
    mapping = {
        "version Family": "originalVersion",
        "MAINTENANCE SUPPORT End": "originalEOLDate",
        "EXTENDED SUPPORT End": "originalExtendedEOLDate",
    }
    extra_date_fields = [
        "FULL SUPPORT Start",
        "FULL SUPPORT End",
        "MAINTENANCE SUPPORT Start",
        "EXTENDED SUPPORT Start",
    ]

    def __init__(self, uuid):
        self.uuid = uuid
        super().__init__()

    def fix_date_formats(self, dataframe: DATAFRAME):
        """Fix date formats.

        :param dataframe: dataframe to fix date formats
        :returns dataframe with date formats fixed
        """
        rename_dict = {
            "Family": ["version"],
            "Start": ["FULL SUPPORT", "MAINTENANCE SUPPORT", "EXTENDED SUPPORT"],
            "End": ["FULL SUPPORT", "MAINTENANCE SUPPORT", "EXTENDED SUPPORT"],
        }

        def rename_column(col: str) -> str:
            """Rename Column.

            :returns renamed column
            """
            if col in rename_dict:
                return rename_dict[col].pop(0) + " " + col
            return col

        dataframe.rename(columns=rename_column, inplace=True)

        dataframe["FULL SUPPORT Start"] = dataframe.apply(
            lambda row: format_date(row["FULL SUPPORT Start"]), axis=1
        )
        dataframe["MAINTENANCE SUPPORT Start"] = dataframe.apply(
            lambda row: format_date(row["MAINTENANCE SUPPORT Start"]), axis=1
        )
        dataframe["EXTENDED SUPPORT Start"] = dataframe.apply(
            lambda row: format_date(row["EXTENDED SUPPORT Start"]), axis=1
        )
        dataframe["FULL SUPPORT End"] = dataframe.apply(
            lambda row: format_date(row["FULL SUPPORT End"]), axis=1
        )

        dataframe["MAINTENANCE SUPPORT End"] = dataframe.apply(
            lambda row: format_date(row["MAINTENANCE SUPPORT End"]), axis=1
        )
        dataframe["EXTENDED SUPPORT End"] = dataframe.apply(
            lambda row: format_date(row["EXTENDED SUPPORT End"]), axis=1
        )

        return dataframe

    def eol_data_generator(self) -> list[dict]:
        """Collect EOL data into a dataframe, convert to json.

        :returns type: list[dict]
        """

        self.goto_url(self.url)

        software_names = web_driver_find_elements(self.driver, "strong")
        software_names = software_names[4:]
        tables = web_driver_find_elements(
            self.driver, "table", {"class": ["tt-table tt-table-dark"]}
        )
        tables_as_df = convert_table_to_pandas_dataframe(tables)

        list_of_dataframes = []

        for sw_name, dataframe in zip(software_names, tables_as_df):
            # While scraping tables from webpage, there could be columns with shared
            # cells which while parsing causes a column name to contain 2 cells.
            # Ex., column name = "Solaris Version Solaris Version" due rowspan=2
            # and there are 2 levels of columns.
            # This normalization is handled by "drop_multilevel_index".
            dataframe = drop_multilevel_index(dataframe)
            dataframe = self.fix_date_formats(dataframe)
            dataframe["originalEolSource"] = self.url
            dataframe["originalName"] = sw_name.text.replace(" Lifecycle Dates", "")
            list_of_dataframes.append(dataframe)

        data = pandas_concat(list_of_dataframes)

        # Minor clean up
        data.drop_duplicates(
            ["originalName", "version Family"], keep="first", inplace=True
        )

        return data
