"""
Extractor module
"""
from parsel import Selector

from sed_parser.extractor.base import PricePageTableContent, Extractor


class SharePriceExtractor(Extractor):
    """SharePriceExtractor"""

    def extract(self) -> PricePageTableContent:
        """extract"""

        html = self._parser_price_table_()

        header = self._parser_table_header_(html)
        body = self._parser_table_body_(html)
        date = self._parser_page_date_()

        return PricePageTableContent(header, body, date)

    def _parser_price_table_(self) -> str:
        """parser price table"""

        html_sel = Selector(self._data)
        table_sel = html_sel.css("div.table-responsive.inner-scroll")

        return (
            table_sel.get()
            .replace("</tbody>", "")
            .replace("</table>", "</tbody></table>")
        )

    def _parser_table_header_(self, html: str) -> list[str]:
        """parser table header"""

        content_sel = Selector(html)

        return content_sel.css("thead > tr > th::text").getall()

    def _parser_table_body_(self, html: str) -> list[list[str]]:
        """parser table body"""

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

    def _parser_page_date_(self) -> str:
        """parser page date"""

        html_sel = Selector(self._data)
        date = html_sel.css("h2.BodyHead.topBodyHead::text").get()
        date = date.replace("Latest Share Price On", "").strip()

        return date
