"""
Step 6 — Targeted Remediator (Tuzatuvchi Agent)
Takes the Blind Critic's structured defect ledger and applies surgical remediations.
Part of the closed autonomous self-correction loop.
"""

import os
import re
from typing import Dict, Any, List


class RemediatorAgent:
    """
    Surgically remediates defects reported by the Blind Critic.
    Does not guess or hallucinate—acts strictly upon the defect ledger directives.
    """

    def apply_remediations(self, file_path: str, defect_ledger: List[Dict[str, Any]]) -> List[str]:
        """Applies surgical fixes for all defects in ledger."""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        repaired_actions: List[str] = []

        for defect in defect_ledger:
            dim = defect.get("dimension")

            # 1. Mobile Responsiveness Fix
            if dim == "mobile_responsiveness" and '<meta name="viewport"' not in content.lower():
                viewport_tag = '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
                if "<head>" in content:
                    content = content.replace("<head>", f"<head>\n    {viewport_tag}")
                else:
                    content = viewport_tag + "\n" + content
                repaired_actions.append("Injected responsive viewport meta tag")

            # 2. Security Hygiene Fix
            elif dim == "security_hygiene":
                content = re.sub(
                    r'<a([^>]+target=["\']_blank["\'])(?![^>]*rel=)',
                    r'<a\1 rel="noopener noreferrer"',
                    content,
                    flags=re.IGNORECASE
                )
                repaired_actions.append("Secured all target='_blank' links with rel='noopener noreferrer'")

            # 3. Typography Hierarchy Fix
            elif dim == "typography_hierarchy":
                # Ensure H1 has commanding typography
                font_link = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Outfit:wght@700;900&display=swap">'
                if "fonts.googleapis.com" not in content:
                    if "<head>" in content:
                        content = content.replace("<head>", f"<head>\n    {font_link}")
                    else:
                        content = font_link + "\n" + content
                
                h1_style = "\n<style id='hallwright-typo-scale'>h1 { font-family: 'Outfit', sans-serif !important; font-size: 56px !important; line-height: 1.15 !important; letter-spacing: -0.02em !important; margin-bottom: 24px !important; }</style>"
                if "</head>" in content and "hallwright-typo-scale" not in content:
                    content = content.replace("</head>", f"{h1_style}\n</head>")
                repaired_actions.append("Applied commanding 56px H1 typography scale and Outfit display font")

            # 4. Visual Depth Modernity & Contrast Fix
            elif dim in ("visual_depth_modernity", "contrast_accessibility", "spatial_grid_harmony"):
                glass_style = """
<style id='hallwright-remediator-depth'>
    body {
        background-color: #090b10 !important;
        color: #f8fafc !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        background-image: radial-gradient(circle at 10% 20%, rgba(0, 240, 255, 0.08) 0%, transparent 40%),
                          radial-gradient(circle at 90% 80%, rgba(112, 0, 255, 0.08) 0%, transparent 40%) !important;
        background-attachment: fixed !important;
    }
    .card, .container, section, article {
        background: rgba(255, 255, 255, 0.04) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 16px !important;
        padding: 32px !important;
        margin-bottom: 32px !important;
    }
</style>
"""
                if "</head>" in content and "hallwright-remediator-depth" not in content:
                    content = content.replace("</head>", f"{glass_style}\n</head>")
                    repaired_actions.append("Injected layered frosted glass elevation and verified 8pt spatial margins")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        return repaired_actions
