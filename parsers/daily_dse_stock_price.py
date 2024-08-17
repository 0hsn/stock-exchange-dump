"""
Daily DSE stock price parser
"""

from datetime import datetime
import sys

from pandas import DataFrame
from parsel import Selector

from hence import Utils, task, group, run_group

from .config import SHARE_PRICE_PATH_FMT

GROUP_NAME = "parse_dse_stock_price"
p_stock_price = group(GROUP_NAME)


@p_stock_price  # 0
@task(title="Parse date on page")
def parse_date_on_page(html, **kwargs) -> str:
    """Find and parse date from page"""

    html_sel = Selector(html)
    date = html_sel.css("h2.BodyHead.topBodyHead::text").get()
    date = date.replace("Latest Share Price On", "").strip()

    return date


@p_stock_price  # 1
@task(title="Parse price table")
def parse_price_table(html, **kwargs) -> str:
    """parser price table"""

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


@p_stock_price  # 2
@task(title="Parse price table headers")
def parse_price_table_headers(**kwargs) -> list[str]:
    """Parse price table headers"""

    tc_html = Utils.get_step(1, GROUP_NAME)

    if not tc_html.result:
        return []

    content_sel = Selector(tc_html.result)
    return content_sel.css("thead > tr > th::text").getall()


@p_stock_price  # 3
@task(title="Parse price table body")
def parse_price_table_body(**kwargs) -> list[list[str]]:
    """Parse price table body"""

    tc_html = Utils.get_step(1, GROUP_NAME)

    if not tc_html.result:
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

    content_sel = Selector(tc_html.result)
    body_sel = content_sel.css("tbody > tr")
    all_data = []

    for tablerow in body_sel:
        table_cells = tablerow.css("tr > td").getall()
        all_data.append(list(map(prepare_cell_data, table_cells)))

    return all_data


@p_stock_price  # 4
@task(title="Prepare csv file path")
def prepare_csv_file_path(**kwargs) -> str:
    """Process CSV filepath"""

    date_str_ = Utils.get_step(0, GROUP_NAME)
    date_ = datetime.strptime(date_str_.result, "%b %d, %Y at %I:%M %p")

    return SHARE_PRICE_PATH_FMT.format(filename=date_.strftime("%Y-%m-%d"))


@p_stock_price  # 5
@task(title="Transform price table data")
def transform_price_table_data(**kwargs) -> None:
    """Convert exported data to pandas.DataFrame"""

    body_ = Utils.get_step(3, GROUP_NAME)
    header_ = Utils.get_step(2, GROUP_NAME)
    filepath_ = Utils.get_step(4, GROUP_NAME)

    # create DataFrame
    df = DataFrame(body_.result, columns=header_.result)

    # remove fields and replace all comma
    df = df.drop(columns=["#", "CHANGE"]).replace({",": ""}, regex=True)
    df.to_csv(filepath_.result, index=False)


if __name__ == "__main__":
    data = sys.stdin.read()

    run_group(
        GROUP_NAME,
        [
            {"html": data},
            {"html": data},
        ],
    )
