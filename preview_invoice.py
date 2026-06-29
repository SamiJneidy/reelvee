"""
Invoice template preview — renders invoice.html with mock data to an HTML file
(and optionally a PDF) so you can inspect the design in a browser without
touching the API.

Usage:
    python preview_invoice.py           # → preview_invoice.html
    python preview_invoice.py --pdf     # → preview_invoice.html + preview_invoice.pdf
"""

import argparse
import webbrowser
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader

# ── Mock data ────────────────────────────────────────────────────────────────

MOCK_CONTEXT = {
    "store": SimpleNamespace(
        currency="SAR",
        config=SimpleNamespace(
            profile=SimpleNamespace(
                title="Storelink Co.",
                bio="Premium e-commerce solutions",
            )
        ),
    ),
    "user": SimpleNamespace(
        email="hello@storelink.io",
        whatsapp_number="+966 50 000 0000",
        address="Riyadh, Saudi Arabia",
    ),
    "invoice": SimpleNamespace(
        invoice_number="INV-000042",
        invoice_hash="a3f9c1d7e2b84056",
        created_at=datetime(2026, 6, 29),
        order_number="000017",
        customer=SimpleNamespace(
            name="Ahmed Al-Rashid",
            email="ahmed@example.com",
            phone="+966 55 123 4567",
            address="Jeddah, Saudi Arabia",
        ),
    ),
    "order": SimpleNamespace(
        items=[
            SimpleNamespace(name="Premium Wireless Headphones", quantity=2, price=299.00, subtotal=598.00),
            SimpleNamespace(name="USB-C Charging Cable (2m)",   quantity=4, price=35.00,  subtotal=140.00),
            SimpleNamespace(name="Leather Phone Case – Black",  quantity=1, price=89.00,  subtotal=89.00),
        ],
        subtotal=827.00,
        discount_amount=50.00,
        shipping_fees=25.00,
        extra_fees=0.00,
        total=802.00,
        notes="Please deliver between 9 AM and 5 PM. Ring the doorbell twice.",
    ),
}

# ── Rendering ─────────────────────────────────────────────────────────────────

TEMPLATE_DIR = Path(__file__).parent / "app" / "shared" / "pdf" / "templates"
OUTPUT_HTML  = Path(__file__).parent / "preview_invoice.html"
OUTPUT_PDF   = Path(__file__).parent / "preview_invoice.pdf"


def render_html() -> str:
    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))
    return env.get_template("invoice.html").render(**MOCK_CONTEXT)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", action="store_true", help="Also generate a PDF via WeasyPrint")
    parser.add_argument("--no-open", action="store_true", help="Do not open the browser automatically")
    args = parser.parse_args()

    html = render_html()
    OUTPUT_HTML.write_text(html, encoding="utf-8")
    print(f"HTML written: {OUTPUT_HTML}")

    if args.pdf:
        from weasyprint import HTML as WeasyprintHTML
        WeasyprintHTML(string=html).write_pdf(str(OUTPUT_PDF))
        print(f"PDF  written: {OUTPUT_PDF}")

    if not args.no_open:
        webbrowser.open(OUTPUT_HTML.as_uri())


if __name__ == "__main__":
    main()
