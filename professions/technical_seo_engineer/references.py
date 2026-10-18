"""
Zane 'The Vector' Sterling - Technical SEO & Growth Engineering Reference Standards.

This module codifies empirical Core Web Vitals thresholds, Schema.org JSON-LD entity structures,
OpenGraph/Twitter card social protocols, and semantic HTML indexability benchmarks.
"""

from typing import Dict, Any, List


CORE_WEB_VITALS_BENCHMARKS: Dict[str, Any] = {
    "max_lcp_seconds": 1.2,
    "max_cls_score": 0.000,
    "max_inp_ms": 100.0,
    "max_ttfb_seconds": 0.3,
    "target_mobile_readiness_pct": 100.0,
    "max_title_length_chars": 60,
    "max_meta_description_chars": 160,
}

SCHEMA_ORG_CANONICAL_ENTITIES: Dict[str, Dict[str, Any]] = {
    "organization": {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Hallwright Systems",
        "url": "https://hallwright.dev",
        "logo": "https://hallwright.dev/assets/logo.png",
        "sameAs": [
            "https://twitter.com/hallwright_dev",
            "https://github.com/kapitan00000978-sketch/hallwright"
        ]
    },
    "website": {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Hallwright Software Studio",
        "url": "https://hallwright.dev",
        "potentialAction": {
            "@type": "SearchAction",
            "target": "https://hallwright.dev/search?q={search_term_string}",
            "query-input": "required name=search_term_string"
        }
    },
    "software_application": {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Hallwright Autonomous Studio",
        "operatingSystem": "All",
        "applicationCategory": "DeveloperApplication",
        "offers": {
            "@type": "Offer",
            "price": "0.00",
            "priceCurrency": "USD"
        }
    }
}

TOXIC_SEO_ANTI_PATTERNS: List[Dict[str, str]] = [
    {
        "id": "multiple_h1_headings",
        "indicator": "Having more than one <h1> element on a single HTML document.",
        "risk": "Dilutes search intent keywords and confuses topical entity models in search engine indexing.",
        "severity": "FATAL"
    },
    {
        "id": "missing_canonical_link",
        "indicator": "Failing to declare an explicit <link rel='canonical' href='...'> tag.",
        "risk": "Exposes URL variations (utm parameters, trailing slashes, sorting) to severe duplicate content penalties.",
        "severity": "FATAL"
    },
    {
        "id": "missing_image_dimensions_cls",
        "indicator": "Rendering <img> tags without explicit width, height, or aspect-ratio attributes.",
        "risk": "Causes sudden layout shifts (CLS > 0.1) as images download, destroying Core Web Vitals rankings.",
        "severity": "FATAL"
    },
    {
        "id": "missing_schema_jsonld",
        "indicator": "HTML document completely devoid of Schema.org JSON-LD structured data scripts.",
        "risk": "Forfeits Google Rich Snippets, Knowledge Graph inclusions, and AI overview visibility.",
        "severity": "HIGH"
    },
    {
        "id": "missing_image_alt_text",
        "indicator": "Rendering <img> elements with empty or omitted alt attributes.",
        "risk": "Damages image search indexing and violates WCAG 2.1 accessibility standards.",
        "severity": "HIGH"
    }
]

CANONICAL_SEO_HEAD_CORE: str = (
    "<!DOCTYPE html>\n"
    '<html lang="en">\n'
    "<head>\n"
    '    <meta charset="UTF-8">\n'
    '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    "    <title>Hallwright — Autonomous Craftsmanship & Engineering Protocol</title>\n"
    '    <meta name="description" content="Hallwright is an autonomous quality protocol embedding Principal-level software, security, and design craftsmanship.">\n'
    '    <link rel="canonical" href="https://hallwright.dev/guide">\n'
    '    <meta name="robots" content="index, follow, max-image-preview:large">\n'
    '    <!-- OpenGraph Social Protocol -->\n'
    '    <meta property="og:title" content="Hallwright — Autonomous Craftsmanship">\n'
    '    <meta property="og:description" content="Principal-level autonomous craftsmanship protocol.">\n'
    '    <meta property="og:url" content="https://hallwright.dev/guide">\n'
    '    <meta property="og:image" content="https://hallwright.dev/og-image.png">\n'
    '    <meta property="og:type" content="website">\n'
    '    <!-- Twitter Card Protocol -->\n'
    '    <meta name="twitter:card" content="summary_large_image">\n'
    '    <meta name="twitter:title" content="Hallwright — Autonomous Craftsmanship">\n'
    '    <meta name="twitter:description" content="Principal-level autonomous craftsmanship protocol.">\n'
    '    <meta name="twitter:image" content="https://hallwright.dev/og-image.png">\n'
    '    <!-- Structured Data (JSON-LD) -->\n'
    '    <script type="application/ld+json">\n'
    "    {\n"
    '        "@context": "https://schema.org",\n'
    '        "@type": "SoftwareApplication",\n'
    '        "name": "Hallwright Protocol",\n'
    '        "applicationCategory": "DeveloperApplication",\n'
    '        "url": "https://hallwright.dev"\n'
    "    }\n"
    "    </script>\n"
    "</head>\n"
    "<body>\n"
    "    <main>\n"
    "        <h1>Autonomous Craftsmanship Architecture</h1>\n"
    '        <img src="hero.webp" width="1200" height="630" alt="Hallwright Engineering Architecture" loading="lazy">\n'
    "        <p>Zero-defect autonomous development protocol.</p>\n"
    "    </main>\n"
    "</body>\n"
    "</html>\n"
)


class SEOReferenceLibrary:
    """Provides empirical Core Web Vitals thresholds, Schema.org entities, and indexability rules."""

    @staticmethod
    def get_core_web_vitals() -> Dict[str, Any]:
        return CORE_WEB_VITALS_BENCHMARKS

    @staticmethod
    def get_schema_entities() -> Dict[str, Dict[str, Any]]:
        return SCHEMA_ORG_CANONICAL_ENTITIES

    @staticmethod
    def get_toxic_anti_patterns() -> List[Dict[str, str]]:
        return TOXIC_SEO_ANTI_PATTERNS

    @staticmethod
    def get_canonical_html_core() -> str:
        return CANONICAL_SEO_HEAD_CORE
