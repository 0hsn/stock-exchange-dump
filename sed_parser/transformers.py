"""
Transformer module
"""


import pandas as pd
from sed_parser.extractor.base import PricePageTableContent


class DataFrameBuilder:
    """Adopter call for data frame"""

    @staticmethod
    def from_price_page_table_content(content: PricePageTableContent) -> pd.DataFrame:
        """Convert content to data frame"""

        df = pd.DataFrame(content.body, columns=content.header)
        return DataFrameMutator.make_stock_price_df(df)


class DataFrameMutator:
    """Mutator class to modify storable data"""

    @staticmethod
    def make_stock_price_df(df: pd.DataFrame) -> pd.DataFrame:
        """make_stock_price_df"""

        # remove fields
        return df.drop(columns=["#", "CHANGE"])
