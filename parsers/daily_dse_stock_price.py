"""
Daily DSE stock price parser
"""

from datetime import datetime
from pathlib import Path
from urllib import request

from hence import Pipeline, PipelineContext
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from pandas import DataFrame
from parsel import Selector

DSE_STOCK_PRICE_PAGE = "https://www.dsebd.org/latest_share_price_scroll_l.php"
SHARE_PRICE_PATH_FMT = "./dumps/dse/share_price/{filename}.csv"

provider = TracerProvider()
processor = BatchSpanProcessor(ConsoleSpanExporter())
provider.add_span_processor(processor)

# Sets the global default tracer provider
trace.set_tracer_provider(provider)

# Creates a tracer from the global tracer provider
tracer = trace.get_tracer("daily.dse.stock_price")

p_stock_price = Pipeline()


@p_stock_price.add_task()
def fetch_content():
    """Fetch the content of example.org"""

    with tracer.start_as_current_span("Fetch-Content") as span:
        with request.urlopen(DSE_STOCK_PRICE_PAGE) as response:
            content = response.read().decode("utf-8")

            span.set_status(trace.StatusCode.OK)
            span.set_attributes({"content.length": len(content)})

            return content


@p_stock_price.add_task(pass_ctx=True)
def parse_date_on_page(ctx: PipelineContext) -> str:
    """Find and parse date from page"""

    with tracer.start_as_current_span("Parse-Date-On-Page") as span:
        html = ctx.result["fetch_content"]
        span.set_attributes({"ctx.result.fetch_content.length": len(html)})

        today = datetime.today().strftime("%Y-%m-%d")

        html_sel = Selector(html)
        date = html_sel.css("h2.BodyHead.topBodyHead::text").get()
        p_today_s = ""

        if date:
            p_today = date.replace("Latest Share Price On", "").strip()
            p_today_d = datetime.strptime(p_today, "%b %d, %Y at %I:%M %p")
            p_today_s = p_today_d.date().strftime("%Y-%m-%d")
            p_today_s = today

            span.set_attribute("today.on_page", p_today_s)

        if today != p_today_s:
            span.set_attributes(
                {
                    "today": today,
                    "today.on_page": p_today_s,
                }
            )

            span.set_status(trace.StatusCode.ERROR)
            raise SystemExit(0)

        span.set_status(trace.StatusCode.OK)
        return p_today_s


@p_stock_price.add_task(pass_ctx=True)
def parse_price_table(ctx: PipelineContext) -> str:
    """parser price table"""

    with tracer.start_as_current_span("Parse-Price-Table") as span:
        html = ctx.result["fetch_content"]
        span.set_attributes({"ctx.result.fetch_content.length": len(html)})

        if not html:
            span.set_status(trace.StatusCode.ERROR)
            return ""

        html_sel = Selector(html)
        table_sel = html_sel.css("div.table-responsive.inner-scroll")

        tbl = table_sel.get()
        if tbl:
            span.add_event("Table-HTML-Fixed")
            span.set_status(trace.StatusCode.OK)

            return tbl.replace("</tbody>", "").replace(
                "</table>",
                "</tbody></table>",
            )

        span.set_status(trace.StatusCode.ERROR)
        return ""


@p_stock_price.add_task(pass_ctx=True)
def parse_price_table_headers(ctx: PipelineContext) -> list[str]:
    """Parse price table headers"""

    with tracer.start_as_current_span("Parse-Price-Table-Headers") as span:
        html = ctx.result["parse_price_table"]
        span.set_attributes({"ctx.result.parse_price_table.length": len(html)})

        if not html:
            span.set_attributes({"header.count": 0})
            span.set_status(trace.StatusCode.ERROR)

            return []

        content_sel = Selector(html)
        lt_head = content_sel.css("thead > tr > th::text").getall()

        span.set_attributes({"header.count": len(lt_head)})
        span.set_status(trace.StatusCode.OK)

        return lt_head


@p_stock_price.add_task(pass_ctx=True)
def parse_price_table_body(ctx: PipelineContext) -> list[list[str]]:
    """Parse price table body"""
    with tracer.start_as_current_span("Parse-Price-Table-Body") as span:
        html = ctx.result["parse_price_table"]
        span.set_attributes({"ctx.result.parse_price_table.length": len(html)})

        if not html:
            span.set_attributes({"raw-html.row.count": 0})
            span.set_status(trace.StatusCode.ERROR)

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

        span.set_attributes({"raw-html.row.count": len(body_sel)})

        all_data = []

        for tablerow in body_sel:
            table_cells = tablerow.css("tr > td").getall()
            all_data.append(list(map(prepare_cell_data, table_cells)))

        span.set_attributes({"data.row.count": len(all_data)})
        span.set_status(trace.StatusCode.OK)

        return all_data


@p_stock_price.add_task(pass_ctx=True)
def prepare_csv_file_path(ctx: PipelineContext) -> str:
    """Process CSV filepath"""
    with tracer.start_as_current_span("Prepare-Csv-File-Path") as span:
        _date = ctx.result["parse_date_on_page"]
        span.set_attributes(
            {
                "ctx.result.parse_date_on_page.length": len(_date),
                "ctx.result.parse_date_on_page": _date,
            }
        )
        span.set_status(trace.StatusCode.OK)

        return SHARE_PRICE_PATH_FMT.format(filename=_date)


@p_stock_price.add_task(pass_ctx=True)
def transform_price_table_data(ctx: PipelineContext) -> None:
    """Convert exported data to pandas.DataFrame"""

    with tracer.start_as_current_span("Transform-Price-Table-Data") as span:
        body_ = ctx.result["parse_price_table_body"]
        header_ = ctx.result["parse_price_table_headers"]
        filepath_ = ctx.result["prepare_csv_file_path"]

        fpath_ = Path(filepath_).resolve()

        span.set_attributes(
            {
                "ctx.result.parse_price_table_body.length": len(body_),
                "ctx.result.parse_price_table_headers.length": len(header_),
                "ctx.result.prepare_csv_file_path": str(fpath_),
            }
        )

        # create DataFrame
        df = DataFrame(body_, columns=header_)
        span.add_event("DF-Created")

        # remove fields and replace all comma
        df = df.drop(columns=["#", "CHANGE"]).replace({",": ""}, regex=True)
        df.to_csv(fpath_, index=False)

        span.add_event("CSV-Created")
        span.set_status(trace.StatusCode.OK)


p_stock_price.run()
