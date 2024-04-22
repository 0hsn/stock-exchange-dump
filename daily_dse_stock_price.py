"""
Daily DSE stock price parser
"""

from datetime import datetime
import sys

from pandas import DataFrame
from parsel import Selector

from hence import AbstractWork, WorkGroup, WorkList, WorkExecFrame, get_step_out

import config


class ParseDateOnPage(AbstractWork):
    """Parse date found on the page"""

    def __work__(self, **kwargs) -> str:
        """Find and parse date from page"""

        html = kwargs.get("html")

        html_sel = Selector(html)
        date = html_sel.css("h2.BodyHead.topBodyHead::text").get()
        date = date.replace("Latest Share Price On", "").strip()

        return date


class ParsePriceTable(AbstractWork):
    """parsing price table"""

    def __work__(self, **kwargs) -> str:
        """parser price table"""
        html = kwargs.get("html")

        if not html:
            return ""

        html_sel = Selector(html)
        table_sel = html_sel.css("div.table-responsive.inner-scroll")

        return (
            table_sel.get()
            .replace("</tbody>", "")
            .replace(
                "</table>",
                "</tbody></table>",
            )
        )


class ParsePriceTableHeaders(AbstractWork):
    """Parse table headers"""

    def __work__(self, **kwargs) -> list[str]:
        html = get_step_out(kwargs, "parse_price_table")

        if not html:
            return []

        content_sel = Selector(html)
        return content_sel.css("thead > tr > th::text").getall()


class ParsePriceTableBody(AbstractWork):
    """parser table body"""

    def __work__(self, **kwargs) -> list[list[str]]:
        html = get_step_out(kwargs, "parse_price_table")

        if not html:
            return []

        def prepare_cell_data(item: str):
            if "displayCompany" in item:
                idx1 = item.index("?name=") + len("?name=")
                item = item[idx1:]

                idx2 = item.index('"')
                return item[:idx2]
            else:
                content_sel = Selector(item)
                return content_sel.css("td::text").get()

        content_sel = Selector(html)
        body_sel = content_sel.css("tbody > tr")
        all_data = []

        for tablerow in body_sel:
            table_cells = tablerow.css("tr > td").getall()
            all_data.append(list(map(prepare_cell_data, table_cells)))

        return all_data


class TransformPriceTableData(AbstractWork):
    """Modify price table data"""

    def __work__(self, **kwargs) -> None:
        """Convert exported data to pandas.DataFrame"""
        body_ = get_step_out(kwargs, "parse_price_table_body")
        header_ = get_step_out(kwargs, "parse_price_table_headers")
        filepath_ = get_step_out(kwargs, "prepare_csv_file_path")

        # create DataFrame
        df = DataFrame(body_, columns=header_)

        # remove fields and replace all comma
        df = df.drop(columns=["#", "CHANGE"]).replace({",": ""}, regex=True)
        df.to_csv(filepath_, index=False)


class PrepareCsvFilePath(AbstractWork):
    """Prepare CSV file path"""

    def __work__(self, **kwargs) -> str:
        """Process CSV filepath"""
        date_str_ = get_step_out(kwargs, "parse_date_on_page")
        date_ = datetime.strptime(date_str_, "%b %d, %Y at %I:%M %p")

        return config.SHARE_PRICE_PATH_FMT.format(filename=date_.strftime("%Y-%m-%d"))


if __name__ == "__main__":
    data = sys.stdin.read()

    wl_dse_parse = WorkList(
        [
            WorkExecFrame(
                id_="parse_date_on_page",
                function=ParseDateOnPage(),
                function_params={"html": data},
            ),
            WorkExecFrame(
                id_="parse_price_table",
                function=ParsePriceTable(),
                function_params={"html": data},
            ),
            WorkExecFrame(
                id_="parse_price_table_headers",
                function=ParsePriceTableHeaders(),
            ),
            WorkExecFrame(
                id_="parse_price_table_body",
                function=ParsePriceTableBody(),
            ),
            WorkExecFrame(
                id_="prepare_csv_file_path",
                function=PrepareCsvFilePath(),
            ),
            WorkExecFrame(
                id_="transform_price_table_data",
                function=TransformPriceTableData(),
            ),
        ]
    )

    wg_dse = WorkGroup(wl_dse_parse)
    wg_dse.execute_dag()
