PROFESSIONAL_PM_TERMS = {
    "objective", "scope", "deliverable", "milestone", "stakeholder", 
    "risk", "kpi", "timeline", "resource", "constraint", "assumption",
    "gap analysis", "sitemap", "navigation", "cta", "call to action"
}

def check_scope(scope):
    issues = []
    if not scope.project_title or len(scope.project_title) < 5:
        issues.append("Project title is too short or missing")
    if len(scope.objectives) < 3:
        issues.append("Fewer than 3 objectives defined")
    if not scope.scope_in:
        issues.append("In-scope boundary not defined")
    if not scope.scope_out:
        issues.append("Out-of-scope/Exclusions not defined")
    if not scope.gap_analysis:
        issues.append("Missing gap analysis (critical for VPM)")
    
    # Check for professional terminology in objectives and scope
    all_text = " ".join(scope.objectives + scope.scope_in + scope.scope_out).lower()
    term_count = sum(1 for term in PROFESSIONAL_PM_TERMS if term in all_text)
    term_coverage = term_count / len(PROFESSIONAL_PM_TERMS)
    
    return {
        "complete": len(issues) == 0,
        "issues": issues,
        "terminology_score": round(term_coverage, 2),
        "status": "PASS" if len(issues) == 0 and term_coverage > 0.3 else "WARNING"
    }

def check_framework(framework):
    issues = []
    # Reference glossary for common web/app pages
    glossary = {"home", "products", "services", "dashboard", "contact", "about", "pricing", "login", "signup"}
    
    if not framework.sitemap:
        issues.append("Sitemap/Navigation hierarchy is empty")
    if not framework.page_details:
        issues.append("Page-by-page detailing is missing")
    if not framework.cta_strategy or len(framework.cta_strategy) < 10:
        issues.append("CTA (Call to Action) strategy is weak or missing")
    
    pages = {str(getattr(item, "page", "")).lower() for item in framework.sitemap}
    coverage = len(pages & glossary) / max(1, len(glossary))
    
    # Check if every sitemap page has a corresponding detail
    detailed_pages = {str(getattr(item, "page", "")).lower() for item in framework.page_details}
    missing_details = pages - detailed_pages
    if missing_details:
        issues.append(f"Missing details for pages: {', '.join(missing_details)}")

    return {
        "complete": len(issues) == 0,
        "issues": issues,
        "glossary_coverage": round(coverage, 2),
        "status": "PASS" if len(issues) == 0 else "WARNING"
    }


