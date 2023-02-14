"""Custom Typehints."""

from bs4.element import ResultSet, Tag
from pandas import DataFrame, Series
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

DATAFRAME = DataFrame
SERIES = Series
WEBDRIVER = WebDriver
RESULTSET = ResultSet
TAG = Tag
WEBELEMENT = WebElement

ListDataFrame = list[DataFrame]
ListWebDriver = list[WebDriver]
ListWebElement = list[WebElement]
