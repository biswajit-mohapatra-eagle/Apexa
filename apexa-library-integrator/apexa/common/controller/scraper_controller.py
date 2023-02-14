"""Scrapers Controller."""

from apexa.common.publisher.publisher_dependency import Publisher
from apexa.common.util import (
    generate_uuid,
    get_logger,
    metadata_entry_points,
    save_to_file,
)

SCRAPPER_ENTRY_POINT_GROUP = "apexa-library-integrator.source"
SCRAPPER_SOURCES = {
    e.name: e for e in metadata_entry_points().select(group=SCRAPPER_ENTRY_POINT_GROUP)
}

LOG = get_logger(__name__)
publisher = Publisher()


def shortlist_scrappers(scrappers: list) -> dict:
    """Select subset of scrappers.

    :param scrappers: list of scrappers

    :returns dictionary metadata entry points of scrappers to use
    """
    scrappers_to_use = {k: v for k, v in SCRAPPER_SOURCES.items() if k in scrappers}
    return scrappers_to_use


def run_scrappers(scrappers: list, test: bool, output_type: str):
    """Run all scrappers in the list.

    :param scrappers: list of scrappers to be run
    :param test: test flag to save results to file
    :param output_type: type of output file
    """
    if scrappers:
        scrappers_to_use = shortlist_scrappers(scrappers)
    else:
        scrappers_to_use = SCRAPPER_SOURCES

    for scrapper, entry_point in scrappers_to_use.items():
        scrapper_upper = scrapper.upper()
        api_class = entry_point.load() if entry_point else None
        if not api_class:
            LOG.info(f"API not found for scrapper ({scrapper_upper})")
            LOG.info(
                f"Scrapper '{scrapper.upper()}' is not available in the current \
                intergrator version,Please update Integrator to the 'latest' version"
            )
            return None

        cls = api_class(generate_uuid())

        LOG.info(f"Fetching data for Scapper: {scrapper_upper}")

        if test:
            # Save data to JSON/CSV file
            eol_data = cls.fetch_scraped_data()
            save_to_file(eol_data, scrapper, output_type)
        else:
            # Send scraped data to MDM
            eol_data = cls.generate_post_feed()
            publisher.publish_software_scraper_data(eol_data)

        LOG.info(f"Ran {scrapper_upper} Successfully")

    return None
