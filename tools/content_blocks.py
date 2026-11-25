"""Documentary content of a wiki page (v9): the article sections and the sources block of an entry page, exactly as
rendered by the shared pipeline function entryContent(). The v2c redesign changes everything around them (header,
banner, info card, side panels) but must not change a single byte of these blocks."""
import re

BLOCKS = re.compile(r'<section class="article-section[\s\S]*?</section>|<section class="sources-block[\s\S]*?</section>')


def article_blocks(html):
    return BLOCKS.findall(html)
