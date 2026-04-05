"""
Generate premium PDF lead magnet: "The 16 Tokens The SEC Just Cleared"
Brand: @big_quiv — dark theme, red accents, gold highlights
"""
from fpdf import FPDF
import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(OUT_DIR, "sec-16-tokens-cleared-breakdown.pdf")

# ── Brand Colors (RGB) ──
BLACK = (10, 10, 15)
DARK_BG = (18, 18, 28)
CARD_BG = (26, 26, 46)
RED = (230, 57, 70)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
LIGHT = (210, 215, 225)
DIMMED = (160, 165, 175)
BLUE = (0, 180, 255)
GREEN = (0, 200, 100)


class SECReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(*DIMMED)
            self.cell(0, 10, "@big_quiv  |  The 16 Tokens The SEC Just Cleared", align="C")
            self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*DIMMED)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def dark_page(self):
        """Fill the entire page background with dark color."""
        self.set_fill_color(*DARK_BG)
        self.rect(0, 0, 210, 297, "F")

    def section_title(self, text, color=RED):
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(*color)
        self.cell(0, 12, text)
        self.ln(8)
        # Red accent line
        self.set_draw_color(*RED)
        self.set_line_width(0.8)
        x = self.get_x()
        y = self.get_y()
        self.line(x, y, x + 50, y)
        self.ln(8)

    def sub_title(self, text, color=GOLD):
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(*color)
        self.cell(0, 10, text)
        self.ln(8)

    def body_text(self, text, bold=False):
        style = "B" if bold else ""
        self.set_font("Helvetica", style, 11)
        self.set_text_color(*LIGHT)
        self.multi_cell(0, 6.5, text)
        self.ln(3)

    def bullet(self, text, bullet_color=RED):
        x = self.get_x()
        y = self.get_y()
        # Bullet dot
        self.set_fill_color(*bullet_color)
        self.ellipse(x + 2, y + 2, 3, 3, "F")
        # Text
        self.set_x(x + 10)
        self.set_font("Helvetica", "", 11)
        self.set_text_color(*LIGHT)
        self.multi_cell(0, 6.5, text)
        self.ln(2)

    def token_row(self, ticker, name, why, tier_color=GOLD):
        x = self.get_x()
        y = self.get_y()
        w = self.w - 2 * self.l_margin

        # Check if we need a new page
        if y > 255:
            self.add_page()
            self.dark_page()
            y = self.get_y()

        # Card background
        self.set_fill_color(*CARD_BG)
        self.rect(x, y, w, 22, "F")

        # Ticker badge
        self.set_fill_color(*tier_color)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*BLACK)
        self.set_xy(x + 3, y + 3)
        tw = self.get_string_width(ticker) + 8
        self.cell(tw, 8, ticker, fill=True, align="C")

        # Name
        self.set_xy(x + tw + 8, y + 3)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(*WHITE)
        self.cell(40, 8, name)

        # Why
        self.set_xy(x + 5, y + 13)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(*DIMMED)
        self.cell(w - 10, 6, why[:100])

        self.set_y(y + 25)

    def highlight_box(self, title, text, accent=RED):
        x = self.get_x()
        y = self.get_y()
        w = self.w - 2 * self.l_margin

        if y > 240:
            self.add_page()
            self.dark_page()
            y = self.get_y()

        # Left accent bar
        self.set_fill_color(*accent)
        self.rect(x, y, 3, 28, "F")

        # Card bg
        self.set_fill_color(30, 30, 50)
        self.rect(x + 3, y, w - 3, 28, "F")

        # Title
        self.set_xy(x + 10, y + 3)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*accent)
        self.cell(0, 7, title)

        # Text
        self.set_xy(x + 10, y + 12)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*LIGHT)
        self.multi_cell(w - 20, 5.5, text)

        self.set_y(y + 32)


def build_pdf():
    pdf = SECReport()
    pdf.alias_nb_pages()

    # ══════════════════════════════════════════════════════════════
    # PAGE 1: COVER
    # ══════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.dark_page()

    # Title block centered
    pdf.ln(60)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 16, "THE 16 TOKENS", align="C")
    pdf.ln(14)
    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(*RED)
    pdf.cell(0, 16, "THE SEC JUST CLEARED", align="C")
    pdf.ln(20)

    # Accent line
    pdf.set_draw_color(*RED)
    pdf.set_line_width(1)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.ln(15)

    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(*DIMMED)
    pdf.cell(0, 8, "The Full Breakdown Most People Missed", align="C")
    pdf.ln(40)

    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(*GOLD)
    pdf.cell(0, 8, "By @big_quiv", align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*DIMMED)
    pdf.cell(0, 6, "Clarity over noise.", align="C")

    # ══════════════════════════════════════════════════════════════
    # PAGE 2: WHAT HAPPENED
    # ══════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.dark_page()

    pdf.section_title("What Actually Happened")
    pdf.body_text(
        "On March 17, 2026, the SEC dropped a 68-page filing that quietly changed "
        "the entire crypto landscape."
    )
    pdf.body_text(
        "They classified 16 tokens as digital commodities. Not securities. Commodities."
    )
    pdf.body_text(
        "That means these tokens are now treated like gold or oil under US law. "
        "No more lawsuits. No more \"is this a security?\" debates. The government "
        "just told you which tokens have a green light."
    )
    pdf.body_text(
        "Most people saw the headline and moved on. They missed the real signal "
        "buried on page 43."
    )

    pdf.ln(5)
    pdf.section_title("What Commodity Status Means")

    items = [
        ("No more securities lawsuits.", "The SEC can no longer sue exchanges or projects for listing these tokens. That legal cloud hanging over crypto since 2020? Gone."),
        ("Exchanges can list freely.", "Coinbase, Kraken, Robinhood can list, promote, and offer trading pairs without fear of enforcement."),
        ("Institutions can buy.", "Hedge funds, pension funds, and asset managers now have regulatory clarity to allocate. This unlocks billions."),
        ("Staking is cleared.", "The filing explicitly states that staking rewards and airdrop distributions under a commodity framework do not trigger securities laws."),
        ("ETF products get the green light.", "BlackRock launched a staked ETH ETF (ETHB) on March 12. Expect more products for SOL, AVAX, and others in Q2."),
    ]
    for title, desc in items:
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*GOLD)
        pdf.cell(0, 7, title)
        pdf.ln(6)
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(*LIGHT)
        pdf.multi_cell(0, 5.5, desc)
        pdf.ln(4)

    # ══════════════════════════════════════════════════════════════
    # PAGE 3: TOKEN LIST — TIER 1 & 2
    # ══════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.dark_page()

    pdf.section_title("All 16 Tokens Classified")

    pdf.sub_title("Tier 1: The Established Giants", WHITE)
    tokens_t1 = [
        ("BTC", "Bitcoin", "The benchmark. Commodity status was already assumed, now it's law."),
        ("ETH", "Ethereum", "The big win. Up 20% since the filing. Staked ETH ETFs now possible."),
        ("LTC", "Litecoin", "Digital silver narrative just got regulatory backing."),
        ("BCH", "Bitcoin Cash", "Fork of BTC. Commodity status follows parent chain logic."),
    ]
    for t, n, w in tokens_t1:
        pdf.token_row(t, n, w, GOLD)

    pdf.ln(5)
    pdf.sub_title("Tier 2: Smart Contract Platforms", BLUE)
    tokens_t2 = [
        ("SOL", "Solana", "Fastest L1. Institutional DeFi products incoming."),
        ("ADA", "Cardano", "Regulatory clarity removes the biggest bear case."),
        ("AVAX", "Avalanche", "Subnet architecture adopted by institutions for tokenized assets."),
        ("DOT", "Polkadot", "Parachain model now has a clear regulatory path."),
        ("ALGO", "Algorand", "Already used by governments. This confirms the positioning."),
        ("ICP", "Internet Computer", "Full-stack blockchain with commodity backing now."),
    ]
    for t, n, w in tokens_t2:
        pdf.token_row(t, n, w, BLUE)

    # ══════════════════════════════════════════════════════════════
    # PAGE 4: TOKEN LIST — TIER 3 & 4
    # ══════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.dark_page()

    pdf.sub_title("Tier 3: Infrastructure Plays", GREEN)
    tokens_t3 = [
        ("LINK", "Chainlink", "Oracle monopoly. 60%+ of DeFi. Now institutions can hold it."),
        ("XLM", "Stellar", "Cross-border payments. Green light for banking integrations."),
        ("FIL", "Filecoin", "Decentralized storage. Enterprise adoption path cleared."),
        ("HBAR", "Hedera", "Enterprise council (Google, IBM, Boeing). This was always the play."),
    ]
    for t, n, w in tokens_t3:
        pdf.token_row(t, n, w, GREEN)

    pdf.ln(5)
    pdf.sub_title("Tier 4: The Wild Cards", RED)
    tokens_t4 = [
        ("XRP", "Ripple", "After years of SEC lawsuits, XRP is finally free. The irony is thick."),
        ("DOGE", "Dogecoin", "Yes, the meme coin. Commodity status means it's here to stay."),
    ]
    for t, n, w in tokens_t4:
        pdf.token_row(t, n, w, RED)

    # ══════════════════════════════════════════════════════════════
    # PAGE 5: PORTFOLIO IMPACT
    # ══════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.dark_page()

    pdf.section_title("Why This Matters For Your Portfolio")

    pdf.sub_title("The Institutional Flood Is Coming")
    pdf.body_text(
        "When BTC got its ETF approval in January 2024, it went from $42K to $73K "
        "in 60 days. That was ONE token getting ONE product."
    )
    pdf.body_text(
        "Now 16 tokens have full commodity status. The financial products that can "
        "be built on top of this are massive:"
    )
    pdf.bullet("Staked ETFs for ETH, SOL, AVAX, and more")
    pdf.bullet("Index funds (imagine a \"SEC-Cleared Crypto Index\")")
    pdf.bullet("Derivatives, options, and structured products")
    pdf.bullet("Pension fund and endowment allocations")
    pdf.body_text("The money hasn't moved yet. But the legal barrier just disappeared.")

    pdf.ln(3)
    pdf.sub_title("The Staking Unlock")
    pdf.body_text(
        "Before this ruling, US-based projects were terrified of offering staking rewards. "
        "The SEC could classify those rewards as securities. That fear is gone."
    )
    pdf.bullet("Higher staking yields as competition increases")
    pdf.bullet("New staking products from centralized exchanges")
    pdf.bullet("Institutional staking services launching Q2 2026")

    pdf.ln(3)
    pdf.sub_title("The Safety Filter")
    pdf.body_text(
        "Here's what nobody is saying out loud: the SEC just told you which tokens "
        "they consider legitimate. Every token NOT on this list is still in legal limbo."
    )
    pdf.body_text(
        "If you're holding tokens that aren't on this list, you're not necessarily in "
        "trouble. But you're holding assets that could face enforcement action. "
        "The risk profile just changed. Use this list as a filter."
    )

    # ══════════════════════════════════════════════════════════════
    # PAGE 6: 3 TOKENS TO WATCH
    # ══════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.dark_page()

    pdf.section_title("3 Tokens To Watch Closest", GOLD)

    pdf.highlight_box(
        "1. ETH (Ethereum)",
        "Staking unlock is the biggest story. BlackRock's ETHB ETF is just the beginning. Watch ETH staking yield vs. Treasury yields.",
        RED
    )
    pdf.highlight_box(
        "2. AVAX (Avalanche)",
        "Nobody's watching this. Subnet architecture adopted by institutions for tokenized RWAs. Regulatory clarity + real utility = undervalued.",
        BLUE
    )
    pdf.highlight_box(
        "3. LINK (Chainlink)",
        "Powers 60%+ of DeFi oracle infrastructure. Every tokenized asset institutions touch needs Chainlink. Watch CCIP adoption numbers.",
        GREEN
    )

    pdf.ln(8)
    pdf.section_title("What Happens Next")

    pdf.highlight_box(
        "March 27, 2026",
        "$13.5B in crypto derivatives expire. Historically triggers 10-15% price swings. Position accordingly.",
        GOLD
    )
    pdf.highlight_box(
        "Q2 2026",
        "The CLARITY Act finalizes stablecoin yield rules. This is the next regulatory domino.",
        GOLD
    )
    pdf.highlight_box(
        "90-Day Window",
        "Institutional liquidity will deepen significantly as fund managers adjust mandates to include these 16 tokens.",
        GOLD
    )

    pdf.body_text(
        "The smart money doesn't react to news. It positions before the crowd catches up."
    )

    # ══════════════════════════════════════════════════════════════
    # PAGE 7: CTA
    # ══════════════════════════════════════════════════════════════
    pdf.add_page()
    pdf.dark_page()

    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(*WHITE)
    pdf.cell(0, 12, "Want Signals Before", align="C")
    pdf.ln(12)
    pdf.set_text_color(*RED)
    pdf.cell(0, 12, "The Crowd Moves?", align="C")
    pdf.ln(20)

    # Accent line
    pdf.set_draw_color(*RED)
    pdf.set_line_width(1)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.ln(15)

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(*LIGHT)
    pdf.multi_cell(0, 7,
        "This is what we do inside Hustler's Krib Signal.\n\n"
        "While most people are reading headlines 48 hours late, our members are "
        "already positioned. We scan the market daily, identify setups with "
        "multi-indicator confluence, and send signals with exact entry, stop loss, "
        "and take profit levels.\n\n"
        "The SEC ruling is public. The setups it creates are not obvious.",
        align="C"
    )

    pdf.ln(15)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(*GOLD)
    pdf.cell(0, 10, "DM me \"KRIB\" on Instagram for access.", align="C")

    pdf.ln(30)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(*DIMMED)
    pdf.cell(0, 6, "@big_quiv  |  Clarity over noise.", align="C")

    # ── Save ──
    pdf.output(OUTPUT_PATH)
    print(f"PDF saved: {OUTPUT_PATH}")
    print(f"Pages: {pdf.page_no()}")


if __name__ == "__main__":
    build_pdf()
