"""Create raw dataset from outer source."""
import logging
from pathlib import Path

import click

from cian_api import (
    get_all_apartment_info_from_json,
    get_ads_by_page_number,
    nested_check,
)
from tqdm import tqdm

# @click.command()
# @click.argument('input_filepath', type=click.Path(exists=True))
# @click.argument('output_filepath', type=click.Path())
# def main(input_filepath, output_filepath):
#     """Create and preprocess dataset from outer source.
#
#     @param input_filepath:
#     @param output_filepath:
#     """
#     logger = logging.getLogger(__name__)
#     logger.info('making final data set from raw data')
#
#
# if __name__ == '__main__':
#     log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
#     logging.basicConfig(level=logging.INFO, format=log_fmt)
#
#     # not used in this stub but often useful for finding various files
#     project_dir = Path(__file__).resolve().parents[2]
#
#     # find .env automagically by walking up directories until it's found, then
#     # load up the .env entries as environment variables
#     load_dotenv(find_dotenv())
#
#     main()


if __name__ == '__main__':
    offers = get_ads_by_page_number(target='sobstv', page=50)
    print(nested_check('seoData', offers)[0])
    # pages = []
    # for page in tqdm(range(1, 23 + 1)):
    #     one_page = get_raw_data_from_api(target='sobstv', page=page)
    #     pages.append(nested_check('offersSerialized', one_page)[0])
