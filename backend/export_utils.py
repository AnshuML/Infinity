from datetime import datetime

def scope_to_markdown(scope):
    lines = []
    lines.append("# PROPOSED SCOPE DOCUMENT")
    lines.append("")
    lines.append("## 1. Project Overview")
    lines.append(f"**Title:** {scope.project_title}")
    lines.append(f"**Date:** {datetime.utcnow().date()}")
    lines.append("**VPM Version:** 1.0")
    lines.append("")
    lines.append("## 2. Requirements Summary")
    lines.append("")
    lines.append("## 3. Scope of Work")
    lines.append("### In-Scope")
    for s in scope.scope_in:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("### Out-of-Scope")
    for s in scope.scope_out:
        lines.append(f"- {s}")
    lines.append("")
    lines.append("## 4. Navigation & Sitemap")
    for n in scope.navigation:
        lines.append(f"- {n}")
    lines.append("")
    lines.append("## 5. Feature Breakdown")
    lines.append("| Feature Name | Description | Priority |")
    lines.append("|--------------|-------------|----------|")
    for obj in scope.objectives:
        lines.append(f"| Objective | {obj} | H |")
    lines.append("")
    lines.append("## 6. Feedback & Approval")
    lines.append("**Reviewer Comments:**")
    for gap in scope.gap_analysis:
        lines.append(f"> {gap}")
    return "\n".join(lines)

def framework_to_markdown(framework):
    lines = []
    lines.append("# CONTENT FRAMEWORK")
    lines.append("")
    lines.append("## 1. Header Navigation")
    lines.append("| Main Nav | Dropdown | Destination | Type | Description | Content Type |")
    lines.append("|----------|----------|-------------|------|-------------|--------------|")
    for item in framework.header_nav:
        lines.append(f"| {item.main_nav} | {item.dropdown} | {item.final_destination} | {item.page_type} | {item.page_description} | {item.content_type} |")
    
    lines.append("")
    lines.append("## 2. Footer Navigation")
    lines.append("| Menu Title | Nested Items | Type | Description | Content Type |")
    lines.append("|------------|--------------|------|-------------|--------------|")
    for item in framework.footer_nav:
        lines.append(f"| {item.menu_title} | {item.nested_items} | {item.page_type} | {item.page_description} | {item.content_type} |")
    
    lines.append("")
    lines.append("## 3. Website Assets")
    lines.append("| Asset Required | Description | Content Type |")
    lines.append("|----------------|-------------|--------------|")
    for item in framework.website_assets:
        lines.append(f"| {item.asset_required} | {item.description} | {item.content_type} |")
        
    lines.append("")
    lines.append("## CTA Strategy")
    lines.append(framework.cta_strategy)
    return "\n".join(lines)

