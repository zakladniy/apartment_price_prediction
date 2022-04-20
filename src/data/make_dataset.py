"""Create raw dataset from outer source."""
import logging

import click
import pandas as pd
from tqdm import tqdm

from .cian_api import (
    get_all_apartment_info_from_json,
    get_ads_by_page_number,
    nested_check,
)

N = 23
TARGET = "sobstv"


@click.command()
@click.argument('output_filepath', type=click.Path())
def main(output_filepath: str) -> None:
    """Create dataset from outer source.

    @param output_filepath: path to external dataset
    """
    logger = logging.getLogger(__name__)
    logger.info('Create dataset from outer source')

    # Extract pages with ads
    pages = []
    for page in tqdm(range(1, N + 1)):
        one_page = get_ads_by_page_number(target=TARGET, page=page)
        pages.append(nested_check('offersSerialized', one_page)[0])

    # Extract ads
    pages_flatten = [item for sublist in pages for item in sublist]
    ads = []
    for ad in tqdm(pages_flatten):
        ads.append(get_all_apartment_info_from_json(ad))

    df = pd.json_normalize(ads)
    df.to_csv(output_filepath, index=False)


if __name__ == '__main__':
    main()
