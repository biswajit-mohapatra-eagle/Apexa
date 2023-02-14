"""Util funtions for apexa library integrator."""

import calendar
import json
import logging
import os
import random
import re
import time
from collections import OrderedDict
from datetime import date, datetime
from decimal import Decimal
from importlib import metadata
from os import path
from typing import Generator, Optional, Union
from uuid import uuid4

from bs4 import BeautifulSoup
from dateutil.parser import parse
from pandas import DataFrame, concat, read_html, to_datetime
from selenium import webdriver
from selenium.webdriver.common.by import By

from apexa.common._typings import (
    DATAFRAME,
    RESULTSET,
    SERIES,
    TAG,
    WEBDRIVER,
    ListDataFrame,
    ListWebElement,
)

MAIN_FIELDS = [
    "originalName",
    "originalVersion",
    "originalBuild",
    "originalVariant",
    "originalEOLDate",
    "originalExtendedEOLDate",
    "originalEolSource",
]

GOOGLE_CACHE_VERSION_URL = "https://webcache.googleusercontent.com/search?q=cache:"

CONFIG_CONTEXT = {"context_settings": {"help_option_names": ["-h", "--help"]}}
APP_NAME = os.environ.get("APP_NAME", "apexa")
DOWNLOAD_PATH = os.environ.get("DOWNLOAD_PATH") or os.getcwd() + "/downloads"

LOG_FILE_INTEGRATIR = os.environ.get(
    "APEXA_INTEGRATOR_LOG_FILE", "/var/log/apexa_integrator.log"
)
LOG_FORMAT = "%(asctime)s %(levelname)-8s [%(name)s] %(message)s"

QUARTER_DATE_PATTERN = r"Q[1-4].*\d{4}"
QUARTER_PATTERN = r"Q[1-4]"
YEAR_PATTERN = r"\d{4}"


def get_logger(name: str):
    """Return a logger with the given name.

    :param name: the name of the logger
    """
    logging.basicConfig(format=LOG_FORMAT, level=logging.INFO)
    return logging.getLogger(name)


# Setup logger
LOG = get_logger(__name__)

# time and date related functions
def sleep_seconds(secs: int):
    """Sleep for the given number of seconds.

    :param secs: the number of seconds to sleep
    """
    return time.sleep(secs)


def get_isoformated_date() -> str:
    """Return the current date in ISO format.

    :returns ISO formatted date
    """
    return datetime.utcnow().isoformat()


def parse_date(timestr: str) -> str:
    """Parsed formatted date str.

    :param timestr: Date string

    :returns parsed date
    """
    try:
        parsed_date = parse(timestr)
        return parsed_date.strftime("%Y-%m-%d")
    except Exception:
        return ""


def format_date(text: str) -> str:
    """Format date string.

    :param text: Date string

    :returns formatted date string
    """
    try:
        # Parse date strings like "Q1 2020", "Q1,2020", "Q1-2020"
        if re.search(QUARTER_DATE_PATTERN, text):
            quarter, year = (
                re.search(QUARTER_PATTERN, text)[0],
                re.search(YEAR_PATTERN, text)[0],
            )
            quarter = int(quarter[1]) * 3
            parsed_date = parse(f"{quarter}-{year}")
            parsed_date = parsed_date.replace(
                day=calendar.monthrange(parsed_date.year, parsed_date.month)[1]
            )
            return parsed_date.date().strftime("%Y-%m-%d")

        if len(text.split(" ")) == 3:
            return parse_date(text)

        if len(text.split(" ")) == 2:
            parsed_date = to_datetime(parse_date(text))
            parsed_date = parsed_date.replace(
                day=calendar.monthrange(parsed_date.year, parsed_date.month)[1]
            )
            return parsed_date.date().strftime("%Y-%m-%d")

        if len(text.split(" ")) == 1:
            parsed_date = datetime(int(text), 12, 31)
            return parsed_date.date().strftime("%Y-%m-%d")

        return ""

    except Exception:
        return ""


def pd_str_replace(
    dataframe_series: SERIES, to_replace: str, value: str, regex: bool = False
) -> SERIES:
    """Replace string occurrences in dataframe column.

    :param dataframe_series: dataframe series
    :param to_replace: string to replace
    :param value: string to replace with
    :param regex: whether to use regex or not [dafault: False]

    :returns dataframe series
    """
    return dataframe_series.str.replace(to_replace, value, regex=regex)


def delete_downloaded_file(file_name: str):
    """Delete auto donwloaded files.

    :param file_name: file name to be deleted
    """
    try:
        os.remove(f"{DOWNLOAD_PATH}/{file_name}")
    except FileNotFoundError:
        LOG.error(f"File not found: {file_name}")
    except Exception as err:
        LOG.exception(err)


# pandas related functions
def list_of_dict_to_pandas_df(data: list[dict]) -> DATAFRAME:
    """Dataframe from list of dict.

    :param data: list of dict data

    :returns dataframe of data
    """
    return DataFrame(data)


def pandas_concat(list_df: ListDataFrame, axis: int = 0) -> DATAFRAME:
    """Concat list of dataframes and create a dataframe.

    :param list_df: list of dataframes
    :param axis: 0: rows, 1: columns

    :returns: combined single dataframe
    """
    return concat(list_df, axis=axis)


def convert_table_to_pandas_dataframe(html_table_elements: list) -> list[DATAFRAME]:
    """Convert html table elements to pandas dataframe.

    :param html_table_elements: list of html table elements
    :returns list of coverted pandas dataframes
    """
    return read_html(str(html_table_elements))


def drop_multilevel_index(dataframe: DATAFRAME, level: int = 0) -> DATAFRAME:
    """Drop multilevel index from dataframe.

    :param dataframe: dataframe
    :returns dataframe without multilevel index
    """
    return dataframe.droplevel(level=level, axis=1)


def combine_multi_index(dataframe: DATAFRAME) -> DATAFRAME:
    """Combine multi index columns to single column.

    :param dataframe: dataframe
    :returns dataframe with combined multi index columns
    """
    dataframe.columns = [
        "_".join(list(OrderedDict.fromkeys(col))) for col in dataframe.columns.values
    ]
    return dataframe


def pandas_df_to_json(dataframe: DATAFRAME) -> list[dict]:
    """Convert dataframe into list of dict with column_name as key.

    :param dataframe: Dataframe to be converted
    :return list_dict: list[dict]
    """
    json_records = dataframe.to_json(orient="records")
    return json.loads(json_records)


def pandas_df_to_csv(dataframe: DATAFRAME, file_name: str = ""):
    """Convert dataframe into a CSV file and saves it to pwd.

    :param dataframe: Dataframe to be converted
    :param file_name: recommended source_type_name as input
    """
    dataframe.to_csv(f"{file_name}_eol_data.csv", index=False)


# os related functions
def os_abspath(file: str) -> str:
    """Return absolute path of a file."""
    return path.abspath(file)


# selenium related functions
def init_chrome_web_driver() -> WEBDRIVER:
    """Create a new instance of Chrome driver for scrapping.

    :return driver: Chrome driver
    """
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": DOWNLOAD_PATH}
    options.add_experimental_option("prefs", prefs)
    options.headless = True
    driver = webdriver.Chrome(
        executable_path=os_abspath("chromedriver"), options=options
    )
    return driver


def get_interactive_element(
    driver: WEBDRIVER,
    find_by: Optional[str] = By.XPATH,
    value: Optional[str] = None,
    is_list: bool = True,
) -> ListWebElement:
    """Find web elements from web which are interactive.

    :param driver: Chrome Driver
    :param find_by: locator strategy
    :param value: locator value
    :param is_list: bool, whether to find multi elements
    """
    return (
        driver.find_elements(find_by, value)
        if is_list
        else driver.find_element(find_by, value)
    )


def web_driver_find_elements(
    driver: WEBDRIVER,
    html_tag: str,
    attributes: dict = None,
    is_list: bool = True,
) -> RESULTSET:
    """Find web elements from web.

    :param driver: Chrome Driver
    :param find_by: locator strategy
    :param value: locator value
    :param is_list: bool, whether to find multi elements
    """
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    attributes = attributes if attributes is not None else {}
    return (
        soup.find_all(html_tag, attributes)
        if is_list
        else soup.find(html_tag, attributes)
    )


def find_inside_element(
    element: TAG, find_html_tag: str, attributes: dict = None, is_list: bool = True
) -> list:
    """Find web elements inside other elements.

    :param element: Parent WebElement Tag
    :param find_html_tag: Target HTML tag
    :param attributes: List of attributes (classname, ids, attributes)
    :param is_list: bool, whether to find multi elements
    """
    attributes = attributes if attributes is not None else {}
    return (
        element.find_all(find_html_tag, attributes)
        if is_list
        else element.find(find_html_tag, attributes)
    )


# json related functions
class CustomEncode(json.JSONEncoder):
    """Custom JSON encoder to handle datetime objects."""

    def default(self, obj):  # pylint: disable=arguments-renamed
        """Override default method to handle datetime objects."""
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        if isinstance(obj, Generator):
            return list(obj)
        if isinstance(obj, bytes):
            try:
                return obj.decode("utf-8")
            except UnicodeDecodeError:
                return repr(obj)

        if isinstance(obj, Decimal):
            return str(obj)

        # We can't encode this object, so we'll just return the default
        LOG.error("Could not encode type %s", type(obj))
        return super().default(obj)


def json_dumps(obj: Union[dict, list], indent: int = None) -> str:
    """Serailize object to json formated str.

    :param obj: object to be JSON serialized
    :param indent: number of spaces to indent the JSON
    :returns json serialized object
    """
    return json.dumps(obj, indent=indent, default=str, cls=CustomEncode)


# random related functions
def random_num_between(min_n: int, max_n: int):
    """Generate a random num between min and max.

    :param min_n: min num
    :param max_n: max num
    :returns num: randon num
    """
    num = random.randrange(min_n, max_n, 1)
    return num


# re related functions
def re_search(pattern: str, text: str):
    """Search for pattern in text, and return the matched str.

    :param text: text str to search regex in
    :param pattern: pattern to be searched
    :returns matched output str
    """
    return re.search(pattern, text)


# metadata related functions
def metadata_entry_points():
    """Return a list of metadata entry points.

    :returns entry_points: list of metadata entry points
    """
    return metadata.entry_points()


def convert_data_to_save_in_file(data: DATAFRAME, filetype: str) -> str:
    """Convert data to file writeable string format.

    :param data: data to be converted
    :param filetype: file type
    :returns file writeable string for respective file type
    """
    data_conversion = {
        "json": json.dumps(pandas_df_to_json(data)),
        "csv": data.to_csv(index=False),
    }
    return data_conversion[filetype]


# Project utils
def save_to_file(data: dict, file_name: str, file_type: str):
    """save data into a file `name`

    :param data: data to be saved
    :param file_name: Output file name
    :param file_type: Output file type
    """
    file_type_lower = file_type.lower()
    with open(f"{file_name}.{file_type_lower}", "w", encoding="utf-8") as outfile:
        outfile.write(convert_data_to_save_in_file(data, file_type.lower()))


def generate_uuid() -> str:
    """Generate a random uuid.

    :returns random uuid
    """
    return str(uuid4())
