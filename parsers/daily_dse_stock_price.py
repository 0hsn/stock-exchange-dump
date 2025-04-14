"""
Daily DSE stock price parser
"""

from datetime import datetime
import sys

from pandas import DataFrame
from parsel import Selector

from hence import Pipeline, PipelineContext


SHARE_PRICE_PATH_FMT = "./dumps/dse/share_price/{filename}.csv"

p_stock_price = Pipeline()


@p_stock_price.add_task()
def parse_date_on_page(html) -> str:
    """Find and parse date from page"""

    html_sel = Selector(html)
    date = html_sel.css("h2.BodyHead.topBodyHead::text").get()

    if date:
        return date.replace("Latest Share Price On", "").strip()

    return ""


@p_stock_price.add_task()
def parse_price_table(html) -> str:
    """parser price table"""

    if not html:
        return ""

    html_sel = Selector(html)
    table_sel = html_sel.css("div.table-responsive.inner-scroll")

    tbl = table_sel.get()
    if tbl:
        return tbl.replace("</tbody>", "").replace(
            "</table>",
            "</tbody></table>",
        )

    return ""


@p_stock_price.add_task(pass_ctx=True)
def parse_price_table_headers(ctx: PipelineContext) -> list[str]:
    """Parse price table headers"""

    tc_html = ctx.result["parse_price_table"]

    if not tc_html:
        return []

    content_sel = Selector(tc_html)
    return content_sel.css("thead > tr > th::text").getall()


@p_stock_price.add_task(pass_ctx=True)
def parse_price_table_body(ctx: PipelineContext) -> list[list[str]]:
    """Parse price table body"""

    tc_html = ctx.result["parse_price_table"]

    if not tc_html:
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

    content_sel = Selector(tc_html)
    body_sel = content_sel.css("tbody > tr")
    all_data = []

    for tablerow in body_sel:
        table_cells = tablerow.css("tr > td").getall()
        all_data.append(list(map(prepare_cell_data, table_cells)))

    return all_data


@p_stock_price.add_task(pass_ctx=True)
def prepare_csv_file_path(ctx: PipelineContext) -> str:
    """Process CSV filepath"""

    date_str_ = ctx.result["parse_date_on_page"]
    date_ = datetime.strptime(date_str_, "%b %d, %Y at %I:%M %p")

    return SHARE_PRICE_PATH_FMT.format(filename=date_.strftime("%Y-%m-%d"))


@p_stock_price.add_task(pass_ctx=True)
def transform_price_table_data(ctx: PipelineContext) -> None:
    """Convert exported data to pandas.DataFrame"""

    body_ = ctx.result["parse_price_table_body"]
    header_ = ctx.result["parse_price_table_headers"]
    filepath_ = ctx.result["prepare_csv_file_path"]

    # create DataFrame
    df = DataFrame(body_, columns=header_)

    # remove fields and replace all comma
    df = df.drop(columns=["#", "CHANGE"]).replace({",": ""}, regex=True)
    df.to_csv(filepath_, index=False)


if __name__ == "__main__":
    data = sys.stdin.read()

    p_stock_price.parameter(parse_date_on_page={"html": data})
    p_stock_price.parameter(parse_price_table={"html": data})

    p_stock_price.run()
