import pytest
from app.services.cms_fingerprinter import (
    fingerprint_cms_static,
    cms_fingerprinter,
)

def test_cms_fingerprint_wordpress():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="generator" content="WordPress 6.4.3" />
        <link rel="stylesheet" href="https://example.com/wp-content/themes/astra/style.css" />
        <script src="https://example.com/wp-content/plugins/elementor/assets/js/frontend.js"></script>
        <script src="https://example.com/wp-content/plugins/contact-form-7/includes/js/index.js"></script>
        <script src="https://example.com/wp-includes/js/jquery/jquery.min.js"></script>
    </head>
    <body>
        <h1>Welcome to WordPress</h1>
    </body>
    </html>
    """
    headers = {
        "server": "nginx/1.24.0",
        "x-powered-by": "PHP/8.2.14"
    }

    result = fingerprint_cms_static(html, headers, "https://example.com")
    assert result["cms_detected"] is True
    assert result["cms_name"] == "WordPress"
    assert result["cms_version"] == "6.4.3"
    assert result["web_server"] == "nginx/1.24.0"
    assert result["runtime"] == "PHP/8.2.14"
    assert "WordPress" in result["technologies"]
    assert "PHP" in result["technologies"]
    assert "Nginx" in result["technologies"]
    assert "jQuery" in result["technologies"]
    assert "elementor" in result["plugins"]
    assert "contact-form-7" in result["plugins"]
    assert result["theme"] == "astra"

def test_cms_fingerprint_shopify():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdn.shopify.com/s/files/1/0000/shop.js"></script>
    </head>
    <body>
        <h1>Storefront</h1>
    </body>
    </html>
    """
    headers = {"server": "cloudflare"}

    result = fingerprint_cms_static(html, headers, "https://myshop.com")
    assert result["cms_detected"] is True
    assert result["cms_name"] == "Shopify"
    assert "Shopify" in result["technologies"]
    assert "Cloudflare" in result["technologies"]

def test_cms_fingerprint_custom():
    html = "<html><body><h1>Minimal static site</h1></body></html>"
    headers = {}

    result = fingerprint_cms_static(html, headers, "https://minimal.com")
    assert result["cms_detected"] is False
    assert result["cms_name"] == "Custom / Jamstack"
    assert len(result["plugins"]) == 0
