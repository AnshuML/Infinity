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
REQUIRED OUTPUT FORMAT:
{
  "header_nav": [
    {
      "main_nav": "Home",
      "dropdown": "",
      "final_destination": "Homepage",
      "page_type": "Main Page",
      "page_description": "Project landing page",
      "key_sections": ["Hero Section", "Features Grid"],
      "content_type": "✒️ Copy"
    }
  ],
  "footer_nav": [
    {
      "menu_title": "Shop",
      "nested_items": ["Category 1", "Category 2"],
      "page_type": "Menu",
      "page_description": "Links to shop categories",
      "key_sections": ["Social Icons"],
      "content_type": "✒️ Copy"
    }
  ],
  "website_assets": [
    {
      "asset_required": "Logo",
      "description": "High-res SVG logo",
      "content_type": "🖼️ Branding"
    }
  ],
  "cta_strategy": "Strategic call to action text..."
}
"""

SIMPLIFIED_SCOPE_FORMAT = """
REQUIRED OUTPUT FORMAT:
{
  "project_title": "Project Name",
  "objectives": ["Goal 1", "Goal 2"],
  "scope_in": ["Included Item 1"],
  "scope_out": ["Excluded Item 1"],
  "navigation": ["Home", "About"],
  "gap_analysis": ["Missing Detail 1"]
}
"""

class ScopeDocument(BaseModel):
    project_title: str = Field(description="The formal title of the project")
    objectives: List[str] = Field(description="List of primary project goals")
    scope_in: List[str] = Field(description="List of items included in project scope")
    scope_out: List[str] = Field(description="List of items explicitly excluded")
    navigation: List[str] = Field(description="Proposed website sitemap/structure")
    gap_analysis: List[str] = Field(description="Identified missing information or risks")

class HeaderNavItem(BaseModel):
    main_nav: Optional[str] = Field("", description="Main Nav Item / Launch Point (e.g. Home, Shop, About)")
    dropdown: Optional[str] = Field("", description="Dropdown / Next Stop (if applicable)")
    final_destination: Optional[str] = Field("", description="Final Destination (e.g. Page Name)")
    page_type: Optional[str] = Field("", description="Type of page (e.g. Main Page, Collection Page, Product Page)")
    page_description: Optional[str] = Field("", description="Brief description of the page purpose")
    key_sections: Optional[Union[str, List[str]]] = Field("", description="Bullet points of key sections/features on this page")
    content_type: Optional[str] = Field("", description="Type of content, usually ‘✒️ Copy’ or ‘🖼️ Image’")

class FooterNavItem(BaseModel):
    menu_title: Optional[str] = Field("", description="Footer Menu Title (e.g. Shop, Quick Links, Policies)")
    nested_items: Optional[Union[str, List[str]]] = Field("", description="Nested Menu Items under this title")
    page_type: Optional[str] = Field("", description="Type of page")
    page_description: Optional[str] = Field("", description="Brief description")
    key_sections: Optional[Union[str, List[str]]] = Field("", description="Bullet points of features")
    content_type: Optional[str] = Field("", description="Type of content")

class WebsiteAsset(BaseModel):
    asset_required: Optional[str] = Field("", description="Name of the asset (e.g. Brand Guidelines, Logo, Product Data)")
    description: Optional[str] = Field("", description="Detailed description of what is needed")
    content_type: Optional[str] = Field("", description="Category (Branding, Image Assets, Copy, etc.)")

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
        """Runs LLM raw and then parses, with recovery"""
        prompt = prompt_template.format(**inputs)
        
        # Create a fresh LLM instance for the call to avoid shared state issues
        # and ensure we aren't using a decommissioned default model
        active_llm = self.llm
        if use_fallback:
            active_llm = self.fallback_llm
            
        try:
            # Explicitly check for llama-3.1-70b-versatile in the active_llm
            # This is a safety check in case LangChain is using a default
            if hasattr(active_llm, 'model_name') and active_llm.model_name == "llama-3.1-70b-versatile":
                active_llm.model_name = "llama-3.3-70b-versatile"
            if hasattr(active_llm, 'model') and active_llm.model == "llama-3.1-70b-versatile":
                active_llm.model = "llama-3.3-70b-versatile"

            res = active_llm.invoke(prompt)
            content = res.content
            
            # Detect and strip code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            # Detect if model returned a schema instead of instance
            if '"properties":' in content or '"$defs":' in content or '"required": [' in content:
                if not is_retry:
                    return self._run_raw(prompt_template, inputs, parser, is_retry=True, use_fallback=True)
            
            try:
                return parser.parse(content)
            except:
                json_match = re.search(r'({.*})', content, re.DOTALL)
                if json_match:
                    return parser.parse(json_match.group(1))
                raise
        except Exception as e:
            if not is_retry:
                return self._run_raw(prompt_template, inputs, parser, is_retry=True, use_fallback=True)
            raise e

    def generate_scope(self, raw_text: str, context: str = "") -> ScopeDocument:
        safe_context = self.truncate_text(context, 4000)
        safe_raw_text = self.truncate_text(raw_text, 6000)
        template = """
        You are an Elite Business Analyst. 
        
        HYBRID STRATEGY:
        1. REFERENCE MATCH: Adopt patterns from 'Reference Examples'. 
        2. BRAIN EXPANSION: Take 'Original Requirements' and expand them strategically.
        
        {format_instructions}
        
        Original Requirements: {raw_text}
        Reference Examples: {context}
        """
        prompt = PromptTemplate(
            template=template,
            input_variables=["raw_text", "context", "format_instructions"],
        )
        return self._run_raw(prompt, {"raw_text": safe_raw_text, "context": safe_context, "format_instructions": SIMPLIFIED_SCOPE_FORMAT}, self.scope_parser)

    def generate_framework(self, scope: ScopeDocument, raw_text: str, context: str = "") -> ContentFramework:
        safe_context = self.truncate_text(context, 4000)
        template = """
        You are a World-Class Virtual Project Manager. Design a COMPREHENSIVE Content Framework.
        
        HYBRID INTELLIGENCE INSTRUCTIONS:
        1. STRUCTURAL DNA: Adopt 'Reference Examples' layout (Tabs, Headers, Emojis).
        2. BRAIN ADDITIONS: Identify project-specific assets and page sections.
        
        {format_instructions}
        
        SCOPE: {scope}
        ORIGINAL NOTES: {raw_text}
        REFERENCE EXAMPLES: {context}
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
