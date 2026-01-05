import os
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import json

load_dotenv()

# Define the structure for a Project Scope Document
class ScopeDocument(BaseModel):
    project_title: str = Field(description="The formal title of the project")
    objectives: list[str] = Field(description="List of primary project goals")
    scope_in: list[str] = Field(description="What is included in the project")
    scope_out: list[str] = Field(description="What is explicitly excluded")
    navigation: list[str] = Field(description="High-level navigation structure (e.g. Home, About, Services)")
    gap_analysis: list[str] = Field(description="Identified missing information or risks")

class SitemapItem(BaseModel):
    page: str = Field(description="The name of the page")
    description: str = Field(description="Brief overview of what this page covers")

class PageDetail(BaseModel):
    page: str = Field(description="The name of the page")
    requirements: str = Field(description="Detailed content and functional requirements for this page")

class ContentFramework(BaseModel):
    sitemap: list[SitemapItem] = Field(description="Hierarchy of pages")
    page_details: list[PageDetail] = Field(description="Content requirements for each page")
    cta_strategy: str = Field(description="Recommended call-to-action strategy")

class AIProcessor:
    def __init__(self, provider: str = "groq", groq_api_key: str = None, google_api_key: str = None):
        self.provider = provider
        groq_key = groq_api_key or os.getenv("GROQ_API_KEY")
        google_key = google_api_key or os.getenv("GOOGLE_API_KEY")
        
        # Using stable Llama 3.3 for reasoning and Gemini Flash for speed/reliability
        if provider == "groq":
            self.llm = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_key)
        elif provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_key)
        else:
            self.llm_groq = ChatGroq(model="llama-3.3-70b-versatile", groq_api_key=groq_key)
            self.llm_gemini = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=google_key)
            
        self.scope_parser = PydanticOutputParser(pydantic_object=ScopeDocument)
        self.framework_parser = PydanticOutputParser(pydantic_object=ContentFramework)

    def truncate_text(self, text: str, max_chars: int = 5000) -> str:
        if len(text) > max_chars:
            return text[:max_chars] + "... [TRUNCATED]"
        return text

    def generate_scope(self, raw_text: str, context: str = "") -> ScopeDocument:
        safe_raw_text = self.truncate_text(raw_text, 4000)
        safe_context = self.truncate_text(context, 2000)
        
        template = """
        You are a Virtual Project Manager. Convert these discussion notes into a formal Scope Document JSON.
        Instructions:
        1. Output ONLY a valid JSON object. 
        2. Do NOT include any explanations, definitions, or code blocks.
        3. Follow this structure strictly: {format_instructions}
        
        REFERENCE EXAMPLES:
        {context}
        
        DISCUSSION NOTES:
        {raw_text}
        """
        prompt = PromptTemplate(
            template=template,
            input_variables=["raw_text", "context"],
            partial_variables={"format_instructions": self.scope_parser.get_format_instructions()},
        )
        
        if self.provider == "hybrid":
            chain_g = prompt | self.llm_groq | self.scope_parser
            chain_m = prompt | self.llm_gemini | self.scope_parser
            a = chain_g.invoke({"raw_text": safe_raw_text, "context": safe_context})
            b = chain_m.invoke({"raw_text": safe_raw_text, "context": safe_context})
            return self.merge_scopes(a, b)
            
        chain = prompt | self.llm | self.scope_parser
        return chain.invoke({"raw_text": safe_raw_text, "context": safe_context})

    def generate_framework(self, scope: ScopeDocument, raw_text: str, context: str = "") -> ContentFramework:
        safe_context = self.truncate_text(context, 2000)
        template = """
        Based on this Project Scope, design a detailed Content Framework JSON.
        Instructions:
        1. Output ONLY a valid JSON object. No schema definitions.
        2. Ensure sitemap, page_details, and cta_strategy fields are present.
        3. Use this format: {format_instructions}
        
        Scope Details: {scope}
        Original Notes: {raw_text}
        Reference Examples: {context}
        """
        prompt = PromptTemplate(
            template=template,
            input_variables=["scope", "raw_text", "context"],
            partial_variables={"format_instructions": self.framework_parser.get_format_instructions()},
        )
        
        if self.provider == "hybrid":
            chain_g = prompt | self.llm_groq | self.framework_parser
            chain_m = prompt | self.llm_gemini | self.framework_parser
            a = chain_g.invoke({"scope": scope.json(), "raw_text": self.truncate_text(raw_text, 2000), "context": safe_context})
            b = chain_m.invoke({"scope": scope.json(), "raw_text": self.truncate_text(raw_text, 2000), "context": safe_context})
            return self.merge_frameworks(a, b)
            
        chain = prompt | self.llm | self.framework_parser
        return chain.invoke({"scope": scope.json(), "raw_text": self.truncate_text(raw_text, 2000), "context": safe_context})

    def merge_scopes(self, a: ScopeDocument, b: ScopeDocument) -> ScopeDocument:
        def dedupe(x):
            seen = set()
            out = []
            for i in x:
                if i not in seen:
                    seen.add(i)
                    out.append(i)
            return out
        return ScopeDocument(
            project_title=a.project_title or b.project_title,
            objectives=dedupe(list(a.objectives) + list(b.objectives)),
            scope_in=dedupe(list(a.scope_in) + list(b.scope_in)),
            scope_out=dedupe(list(a.scope_out) + list(b.scope_out)),
            navigation=dedupe(list(a.navigation) + list(b.navigation)),
            gap_analysis=dedupe(list(a.gap_analysis) + list(b.gap_analysis))
        )

    def merge_frameworks(self, a: ContentFramework, b: ContentFramework) -> ContentFramework:
        def get_v(item, key, default=""):
            if isinstance(item, dict): return item.get(key, default)
            return getattr(item, key, default)

        def dedupe_items(items):
            seen = set()
            out = []
            for item in items:
                p, d, r = get_v(item, 'page'), get_v(item, 'description'), get_v(item, 'requirements')
                k = (p, d, r)
                if k not in seen:
                    seen.add(k); out.append(item)
            return out
            
        sitemap = dedupe_items(list(a.sitemap) + list(b.sitemap))
        page_details = dedupe_items(list(a.page_details) + list(b.page_details))
        cta = (a.cta_strategy or "")
        if b.cta_strategy: cta = cta + (" | " if cta else "") + b.cta_strategy
        return ContentFramework(sitemap=sitemap, page_details=page_details, cta_strategy=cta)
