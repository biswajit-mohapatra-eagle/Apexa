"""Scraper model class."""

from abc import ABC, ABCMeta

from apexa.common._typings import DATAFRAME
from apexa.common.util import (
    GOOGLE_CACHE_VERSION_URL,
    MAIN_FIELDS,
    delete_downloaded_file,
    init_chrome_web_driver,
    pandas_concat,
    pandas_df_to_json,
    sleep_seconds,
)


class Scraper(metaclass=ABCMeta):
    """Scraper Class."""

    url = None
    name = None
    uuid = None
    supports_download = False
    downloaded_file_name = ""
    scraping_restricted = False
    mapping = {}
    extra_date_fields = []

    def __init__(self):
        self.driver = init_chrome_web_driver()

    def __del__(self):
        """Destructor to close browser and clean files."""
        self.close_browser()

    def close_browser(self):
        """Close browser."""
        if self.supports_download:
            delete_downloaded_file(self.downloaded_file_name)
        self.driver.quit()

    def close_tab(self):
        """Close browser tab."""
        self.driver.close()

    def focus_tab(self, number: int):
        """Switch to tab number.

        :param number: Tab number
        """
        focus_page = self.driver.window_handles[number]
        self.driver.switch_to.window(focus_page)

    def new_tab(self):
        """Open new tab."""
        current_tab = self.driver.current_window_handle
        self.driver.execute_script("window.open('');")
        all_tabs = self.driver.window_handles
        for tab in all_tabs:
            if tab != current_tab:
                self.driver.switch_to.window(tab)
                break

    def goto_url(self, url: str, sec: int = 0):
        """Go to URL.

        :param url: url to visit to
        :param sec: wait time to load the page
        """
        url = f"{GOOGLE_CACHE_VERSION_URL}{url}" if self.scraping_restricted else url
        self.driver.get(url)
        sleep_seconds(sec)

    def format_data(self, scraped_data: DATAFRAME) -> DATAFRAME:
        """Format dataframe data to include addition dates and columns.

        :param dataframe: Scraper Data
        :return: Formatted dataframe in sharable format to MDM
        """
        scraped_data = scraped_data.rename(columns=self.mapping)

        main_columns = list(set(scraped_data.columns) & set(MAIN_FIELDS))
        extra_date_columns = list(
            set(scraped_data.columns) & set(self.extra_date_fields)
        )
        extra_columns = list(
            set(scraped_data.columns) - set(main_columns + self.extra_date_fields)
        )

        main_df = scraped_data[main_columns].copy()
        extra_dates_df = scraped_data[extra_date_columns].copy()
        extra_columns_df = scraped_data[extra_columns].copy()

        if len(extra_dates_df.columns):
            dates_data = extra_dates_df.to_dict(orient="records")
            main_df.loc[:, "extraDates"] = dates_data

        if len(extra_columns_df.columns):
            dates_data = extra_columns_df.to_dict(orient="records")
            main_df.loc[:, "extraFields"] = dates_data

        del scraped_data
        del extra_dates_df
        del extra_columns_df

        main_df.loc[:, "scraperName"] = self.name
        main_df.loc[:, "scraperId"] = self.uuid
        return main_df

    def fetch_scraped_data(self) -> DATAFRAME:
        """Data to be sent in EOL post request.

        :retruns scraped data
        """
        scraped_data: DATAFRAME = self.eol_data_generator()
        return scraped_data

    def generate_post_feed(self) -> dict:
        """Generate EOL post feed to be sent to MDM.

        :returns scraped data as dictionary
        """
        scraped_data = self.fetch_scraped_data()
        scraped_data = self.format_data(scraped_data)
        return pandas_df_to_json(scraped_data)

    def eol_data_generator(self) -> DATAFRAME:
        """Generates eol_data, to be implemented by subclasses."""
        return DATAFRAME

    def extract_version(self, text: str) -> str:  # pylint: disable=W0613
        """Extract version from text, to be implemented by subclasses.

        :param text: text to extract version from
        """
        return ""


class MultiURLScraper(Scraper, ABC):
    """Scraper to handle multiple urls."""

    urls = None

    # Override
    def fetch_scraped_data(self) -> DATAFRAME:
        """Data to be sent in EOL post request.

        :retruns scraped data
        """
        list_eol_data = []
        for url in self.urls:
            super().__init__()
            self.url = url
            scraped_data = self.eol_data_generator()
            list_eol_data.append(scraped_data)

        scraped_data = pandas_concat(list_eol_data)
        return scraped_data
