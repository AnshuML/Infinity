import os
import re
from typing import List, Optional, Union
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

# Simplified Format Instructions to prevent LLM schema regurgitation
SIMPLIFIED_FRAMEWORK_FORMAT = """
CRITICAL: Output MUST be valid JSON ONLY. No markdown, no asterisks, no bullets, no headers.

REQUIRED OUTPUT FORMAT (Pure JSON):
{
  "header_nav": [
    {
      "main_nav": "Home",
      "dropdown": "",
      "final_destination": "Homepage",
      "page_type": "Main Page",
      "page_description": "Project landing page",
       "key_sections": ["Hero Section", "Service Overview", "Social Proof Grid"],
      "content_type": "Copy",
      "content_link": "",
      "status": "Not Started",
      "client_notes": ""
    },
    {
      "main_nav": "Shop",
      "dropdown": "Collections",
      "final_destination": "All Products Page",
      "page_type": "Collection",
      "page_description": "Grid of all items",
      "key_sections": ["Filter Sidebar", "Product Cards", "Newsletter"],
      "content_type": "Copy/Images",
      "content_link": "",
      "status": "Not Started",
      "client_notes": ""
    }
  ],
  "footer_nav": [
    {
      "menu_title": "Quick Links",
      "nested_items": ["About Us", "Contact Us", "Terms of Service"],
      "page_type": "Information",
      "page_description": "Company legal and info links",
      "key_sections": ["Copyright Notice", "Language Toggle"],
      "content_type": "Copy",
      "content_link": "",
      "status": "Not Started",
      "client_notes": ""
    },
    {
      "menu_title": "Sustainability",
      "nested_items": ["Impact Report", "Our Process"],
      "page_type": "Strategy",
      "page_description": "Brand values and ethics",
      "key_sections": ["Eco Badge", "Timeline"],
      "content_type": "Copy/Images",
      "content_link": "",
      "status": "Not Started",
      "client_notes": ""
    }
  ],
  "website_assets": [
    {
      "asset_required": "Logo",
      "description": "High-res SVG logo",
      "content_type": "Branding",
      "content_link": "",
      "status": "Not Started",
      "client_notes": ""
    }
  ],
  "cta_strategy": "Strategic call to action text..."
}
"""

SIMPLIFIED_SCOPE_FORMAT = """
CRITICAL: Output MUST be valid JSON ONLY. No markdown, no asterisks, no bullets, no headers.

REQUIRED OUTPUT FORMAT (Pure JSON):
{
  "project_title": "Project Name",
  "objectives": ["Goal 1 (e.g. Expand reach)", "Goal 2 (e.g. Optimize conversion)"],
  "scope_in": ["Module 1", "Module 2", "Module 3"],
  "scope_out": ["Exclusion 1", "Exclusion 2"],
  "navigation": ["Home", "About", "Services", "Portfolio", "Contact"],
  "gap_analysis": ["Missing Detail 1", "Risk Factor 2", "Assumption 3"],
  "strategic_recommendations": ["Recommendation 1", "Technical Tip 2", "Marketing Suggestion 3"]
}
"""

class ScopeDocument(BaseModel):
    project_title: str = Field(description="The formal title of the project")
    objectives: List[str] = Field(description="List of primary project goals")
    scope_in: List[str] = Field(description="List of items included in project scope")
    scope_out: List[str] = Field(description="List of items explicitly excluded")
    navigation: List[str] = Field(description="Proposed website sitemap/structure")
    gap_analysis: List[str] = Field(description="Identified missing information or risks")
    strategic_recommendations: List[str] = Field(default_factory=list, description="Expert tips and strategic advice from the AI")

class HeaderNavItem(BaseModel):
    main_nav: Optional[str] = Field("", description="Main Nav Item / Launch Point (e.g. Home, Shop, About)")
    dropdown: Optional[str] = Field("", description="Dropdown / Next Stop (if applicable)")
    final_destination: Optional[str] = Field("", description="Final Destination (e.g. Page Name)")
    page_type: Optional[str] = Field("", description="Type of page (e.g. Main Page, Collection Page, Product Page)")
    page_description: Optional[str] = Field("", description="Brief description of the page purpose")
    key_sections: Optional[Union[str, List[str]]] = Field("", description="Bullet points of key sections/features on this page")
    content_type: Optional[str] = Field("", description="Type of content, usually ‘✒️ Copy’ or ‘🖼️ Image’")
    content_link: Optional[str] = Field("", description="Link to the content asset")
    status: Optional[str] = Field("Not Started", description="Current status")
    client_notes: Optional[str] = Field("", description="Additional notes")

class FooterNavItem(BaseModel):
    menu_title: Optional[str] = Field("", description="Footer Menu Title (e.g. Shop, Quick Links, Policies)")
    nested_items: Optional[Union[str, List[str]]] = Field("", description="Nested Menu Items under this title")
    page_type: Optional[str] = Field("", description="Type of page")
    page_description: Optional[str] = Field("", description="Brief description")
    key_sections: Optional[Union[str, List[str]]] = Field("", description="Bullet points of features")
    content_type: Optional[str] = Field("", description="Type of content")
    content_link: Optional[str] = Field("", description="Link to the content asset")
    status: Optional[str] = Field("Not Started", description="Current status")
    client_notes: Optional[str] = Field("", description="Additional notes")

class WebsiteAsset(BaseModel):
    asset_required: Optional[str] = Field("", description="Name of the asset (e.g. Brand Guidelines, Logo, Product Data)")
    description: Optional[str] = Field("", description="Detailed description of what is needed")
    content_type: Optional[str] = Field("", description="Category (Branding, Image Assets, Copy, etc.)")
    content_link: Optional[str] = Field("", description="Link to the content asset")
    status: Optional[str] = Field("Not Started", description="Current status of the asset")
    client_notes: Optional[str] = Field("", description="Additional notes or feedback from the client")

class ContentFramework(BaseModel):
    header_nav: list[HeaderNavItem] = Field(description="Items for the Header Navigation tab")
    footer_nav: list[FooterNavItem] = Field(description="Items for the Footer Navigation tab")
    website_assets: list[WebsiteAsset] = Field(description="Items for the Website Assets tab")
    cta_strategy: str = Field(description="Recommended call-to-action strategy for the entire site")

class AIProcessor:
    def __init__(self, provider: str = "groq", groq_api_key: str = None, google_api_key: str = None):
        self.provider = provider
        groq_key = groq_api_key or os.getenv("GROQ_API_KEY")
        google_key = google_api_key or os.getenv("GOOGLE_API_KEY")

        # Tiered Groq Strategy for 100% Reliability
        # Llama 3.3 70B is the latest stable. 
        # Fallback to 8B instant since it has high rate limits and is always available.
        try:
            self.primary_llm = ChatGroq(model_name="llama-3.3-70b-versatile", groq_api_key=groq_key)
            self.fallback_llm = ChatGroq(model_name="llama-3.1-8b-instant", groq_api_key=groq_key)
            print(f"INFO: Groq initialized with llama-3.3-70b-versatile and 8b fallback.")
        except Exception as e:
            print(f"WARNING: Groq init failed: {e}. Falling back to default settings.")
            self.primary_llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_key)
            self.fallback_llm = ChatGroq(model="llama-3.1-8b-instant", groq_api_key=groq_key)

        self.gemini_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", google_api_key=google_key)
        
        # Respect user choice 
        if provider == "gemini":
            self.llm = self.gemini_llm
        else:
            self.llm = self.primary_llm
            
        self.scope_parser = PydanticOutputParser(pydantic_object=ScopeDocument)
        self.framework_parser = PydanticOutputParser(pydantic_object=ContentFramework)

    def truncate_text(self, text: str, max_chars: int = 5000) -> str:
        if len(text) > max_chars:
            return text[:max_chars] + "... [TRUNCATED]"
        return text

    def _run_raw(self, prompt_template, inputs, parser, is_retry=False, use_fallback=False):
        """Runs LLM raw and then parses, with recovery and aggressive JSON extraction"""
        prompt = prompt_template.format(**inputs)
        
        # Create a fresh LLM instance for the call to avoid shared state issues
        active_llm = self.llm
        if use_fallback:
            active_llm = self.fallback_llm
            
        try:
            # Explicitly check for deprecated models
            if hasattr(active_llm, 'model_name') and active_llm.model_name == "llama-3.1-70b-versatile":
                active_llm.model_name = "llama-3.3-70b-versatile"
            if hasattr(active_llm, 'model') and active_llm.model == "llama-3.1-70b-versatile":
                active_llm.model = "llama-3.3-70b-versatile"

            res = active_llm.invoke(prompt)
            content = res.content
            
            # ===== STRATEGY 1: Remove markdown code blocks =====
            if "```json" in content:
                parts = content.split("```json")
                if len(parts) > 1:
                    content = parts[1].split("```")[0].strip()
            elif "```" in content:
                parts = content.split("```")
                if len(parts) >= 2:
                    content = parts[1].strip()
            
            # ===== STRATEGY 2: Extract content between first { and last } =====
            first_brace = content.find('{')
            last_brace = content.rfind('}')
            if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                content = content[first_brace:last_brace+1]
            
            # ===== STRATEGY 3: Clean up common LLM artifacts =====
            # Remove text before JSON starts
            content = content.strip()
            if content and not content.startswith('{'):
                # Try to find where JSON actually starts
                json_start = content.find('{')
                if json_start > 0:
                    content = content[json_start:]
            
            # Remove text after JSON ends
            if content and not content.endswith('}'):
                json_end = content.rfind('}')
                if json_end > 0:
                    content = content[:json_end+1]
            
            # ===== STRATEGY 4: Detect schema regurgitation =====
            # If LLM returned schema definition instead of data
            schema_indicators = ['"properties":', '"$defs":', '"definitions":', '"type": "object"']
            is_schema = any(indicator in content for indicator in schema_indicators)
            
            if is_schema and not is_retry:
                print("⚠️ LLM returned schema instead of data. Retrying with fallback model...")
                return self._run_raw(prompt_template, inputs, parser, is_retry=True, use_fallback=True)
            
            # ===== STRATEGY 5: Try parsing with LangChain parser =====
            try:
                return parser.parse(content)
            except Exception as parse_err:
                print(f"⚠️ Parser failed: {str(parse_err)[:100]}... Trying fallback extraction")
                
                # ===== STRATEGY 6: Regex-based JSON extraction =====
                # Try to extract outermost JSON object with nested braces support
                json_pattern = r'\{(?:[^{}]|(?:\{(?:[^{}]|(?:\{[^{}]*\}))*\}))*\}'
                json_matches = re.findall(json_pattern, content, re.DOTALL)
                
                if json_matches:
                    # Try the largest match first (likely the complete object)
                    json_matches.sort(key=len, reverse=True)
                    for match in json_matches:
                        try:
                            return parser.parse(match)
                        except:
                            continue
                
                # ===== STRATEGY 7: Manual JSON parsing as last resort =====
                try:
                    import json as json_lib
                    parsed_json = json_lib.loads(content)
                    # If we got valid JSON, try to convert it to the expected model
                    return parser.parse(json_lib.dumps(parsed_json))
                except:
                    pass
                
                # All strategies failed
                raise parse_err
                
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error in _run_raw: {error_msg[:200]}")
            
            # Retry with fallback model if not already done
            if not is_retry:
                print("🔄 Retrying with fallback model...")
                return self._run_raw(prompt_template, inputs, parser, is_retry=True, use_fallback=True)
            
            # If retry also failed, provide helpful error message
            print("❌ Both primary and fallback models failed. Check your prompt and model configuration.")
            raise RuntimeError(f"OUTPUT_PARSING_FAILURE: Unable to parse LLM output after multiple attempts. Last error: {error_msg}")

    def generate_scope(self, raw_text: str, context: str = "") -> ScopeDocument:
        safe_context = self.truncate_text(context, 4000)
        safe_raw_text = self.truncate_text(raw_text, 6000)
        template = """
You are a Business Analyst. Generate a structured JSON scope document.

🚨 CRITICAL OUTPUT RULES:
- Return ONLY valid JSON. Start with {{ and end with }}
- NO markdown code blocks (no ```json or ```)
- NO explanatory text before or after the JSON
- NO asterisks, bullets, or headers

INSTRUCTIONS:
1. Study the Reference Examples and adopt their depth and terminology.
2. Expand the Original Requirements comprehensively.
3. Generate comprehensive lists (minimum 3-5 items per field).
4. Be specific and detailed in descriptions.

{format_instructions}

Original Requirements:
{raw_text}

Reference Examples:
{context}
        """
        prompt = PromptTemplate(
            template=template,
            input_variables=["raw_text", "context", "format_instructions"],
        )
        return self._run_raw(prompt, {"raw_text": safe_raw_text, "context": safe_context, "format_instructions": SIMPLIFIED_SCOPE_FORMAT}, self.scope_parser)

    def generate_framework(self, scope: ScopeDocument, raw_text: str, context: str = "") -> ContentFramework:
        safe_context = self.truncate_text(context, 4000)
        template = """
You are a Virtual Project Manager. Generate a comprehensive content framework.

🚨 CRITICAL OUTPUT RULES:
- Return ONLY valid JSON. Start with {{ and end with }}
- NO markdown code blocks (no ```json or ```)
- NO explanatory text before or after the JSON
- NO asterisks, bullets, or headers

INSTRUCTIONS:
1. Study the Reference Examples and match their structure and depth.
2. Identify ALL pages, navigation items, and assets comprehensively.
3. Include at least 5-8 header_nav items, 3-5 footer_nav items, and 5+ website_assets.
4. Fill out EVERY field with meaningful, specific content.
5. Make key_sections arrays with 3-5 items each.

{format_instructions}

SCOPE:
{scope}

ORIGINAL NOTES:
{raw_text}

REFERENCE EXAMPLES:
{context}
        """
        prompt = PromptTemplate(
            template=template,
            input_variables=["scope", "raw_text", "context", "format_instructions"],
        )
        return self._run_raw(prompt, {"scope": scope.json(), "raw_text": self.truncate_text(raw_text, 2000), "context": safe_context, "format_instructions": SIMPLIFIED_FRAMEWORK_FORMAT}, self.framework_parser)

    def merge_scopes(self, a: ScopeDocument, b: ScopeDocument) -> ScopeDocument:
        def dedupe(x):
            seen = set()
            out = []
            for i in x:
                val = i
                if isinstance(i, list):
                    val = "|".join(map(str, i))
                if val not in seen:
                    seen.add(val)
                    out.append(i)
            return out
            
        return ScopeDocument(
            project_title=a.project_title,
            objectives=dedupe(a.objectives + b.objectives),
            scope_in=dedupe(a.scope_in + b.scope_in),
            scope_out=dedupe(a.scope_out + b.scope_out),
            navigation=dedupe(a.navigation + b.navigation),
            gap_analysis=dedupe(a.gap_analysis + b.gap_analysis)
        )

    def merge_frameworks(self, a: ContentFramework, b: ContentFramework) -> ContentFramework:
        def get_v(obj, key):
            if hasattr(obj, key): return getattr(obj, key)
            if isinstance(obj, dict): return obj.get(key)
            return ""

        def dedupe_list(items, keys):
            seen = set()
            out = []
            for item in items:
                vals = []
                for key in keys:
                    v = get_v(item, key)
                    if isinstance(v, (list, dict)):
                        v = str(v)
                    vals.append(v)
                k = tuple(vals)
                if k not in seen:
                    seen.add(k)
                    out.append(item)
            return out

        return ContentFramework(
            header_nav=dedupe_list(a.header_nav + b.header_nav, ['main_nav', 'dropdown', 'final_destination']),
            footer_nav=dedupe_list(a.footer_nav + b.footer_nav, ['menu_title', 'nested_items']),
            website_assets=dedupe_list(a.website_assets + b.website_assets, ['asset_required']),
            cta_strategy=a.cta_strategy,
            project_title=getattr(a, 'project_title', getattr(b, 'project_title', '')),
            objectives=getattr(a, 'objectives', getattr(b, 'objectives', [])),
            scope_in=getattr(a, 'scope_in', getattr(b, 'scope_in', [])),
            scope_out=getattr(a, 'scope_out', getattr(b, 'scope_out', [])),
            navigation=getattr(a, 'navigation', getattr(b, 'navigation', [])),
            gap_analysis=getattr(a, 'gap_analysis', getattr(b, 'gap_analysis', []))
        )
