import streamlit as st
import os
import sys

# Add backend to path so we can import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

from ai_processor import AIProcessor
from validation_engine import ValidationEngine
from data_utils import read_docx, read_pdf, read_xlsx

def get_example_paths(data_dir):
    out = []
    if not os.path.exists(data_dir):
        return out
    for item in os.listdir(data_dir):
        item_path = os.path.join(data_dir, item)
        if os.path.isdir(item_path) and item.startswith("Example"):
            input_dir = os.path.join(item_path, "input")
            output_dir = os.path.join(item_path, "output")
            input_files = []
            output_files = []
            if os.path.exists(input_dir):
                for f in os.listdir(input_dir):
                    input_files.append(os.path.join(input_dir, f))
            if os.path.exists(output_dir):
                for f in os.listdir(output_dir):
                    output_files.append(os.path.join(output_dir, f))
            out.append({
                "name": item,
                "input_files": input_files,
                "output_files": output_files
            })
    return out
from export_utils_excel import framework_to_excel, scope_to_excel, get_header_nav_excel, get_footer_nav_excel, get_website_assets_excel, get_blank_framework_excel
from quality_checks import check_scope, check_framework

def safe_get_attr(obj, attr, default="Unknown"):
    try:
        if isinstance(obj, dict):
            return obj.get(attr, default)
        return getattr(obj, attr, default)
    except:
        return default

st.set_page_config(page_title="VPM - Virtual Project Manager", layout="wide")

# Premium UI Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Outfit:wght@400;700&display=swap');
    
    :root {
        --primary: #6366f1;
        --secondary: #a855f7;
        --bg-dark: #0f172a;
        --card-bg: rgba(30, 41, 59, 0.7);
        --text-muted: #94a3b8;
    }

    /* Force Streamlit Variables */
    [data-testid="stAppViewContainer"] {
        background-color: var(--bg-dark);
        color: #f8fafc !important;
    }

    /* Hide the white header */
    header[data-testid="stHeader"] {
        background-color: rgba(15, 23, 42, 0.8) !important;
        backdrop-filter: blur(10px);
    }

    html, body, [class*="css"], .stMarkdown, p, span, h1, h2, h3, h4, label {
        font-family: 'Inter', sans-serif;
        color: #f8fafc !important;
    }
    
    .stApp {
        background: radial-gradient(circle at 20% 10%, rgba(99, 102, 241, 0.15), transparent),
                    radial-gradient(circle at 80% 80%, rgba(168, 85, 247, 0.15), transparent),
                    #0f172a !important;
    }
    
    .main-header {
        font-family: 'Outfit', sans-serif;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem;
        font-weight: 800;
        margin-bottom: 0px;
        letter-spacing: -1px;
        animation: fadeInDown 0.8s ease-out;
    }

    /* Force radio/checkbox labels are visible */
    [data-testid="stWidgetLabel"] p {
        color: #f8fafc !important;
    }

    /* File Uploader Dark Force */
    [data-testid="stFileUploader"] {
        background-color: rgba(30, 41, 59, 0.5) !important;
        border: 2px dashed rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        padding: 10px !important;
    }
    
    [data-testid="stFileUploader"] section {
        background-color: transparent !important;
    }

    [data-testid="stFileUploader"] label, [data-testid="stFileUploader"] p, [data-testid="stFileUploader"] span {
        color: #f8fafc !important;
    }

    /* Input/Text Area Dark Force */
    .stTextArea textarea, .stTextInput input {
        background-color: rgba(15, 23, 42, 0.6) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Selectbox/Dropdown Dark Force */
    [data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.6) !important;
    }
    [data-baseweb="select"] * {
        color: #f8fafc !important;
    }
    [data-testid="stVirtualDropdown"] li {
        background-color: #1e293b !important;
        color: #f8fafc !important;
    }

    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .card {
        background: var(--card-bg);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4);
        transition: transform 0.3s ease, border 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
        border: 1px solid rgba(99, 102, 241, 0.4);
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        color: white !important;
        border: none;
        padding: 14px;
        border-radius: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
    }
    
    .stButton>button:hover {
        transform: scale(1.02) translateY(-2px);
        box-shadow: 0 10px 25px rgba(99, 102, 241, 0.5);
    }

    .stButton>button:active {
        transform: scale(0.98);
    }

    /* Intelligence Trace Pulse */
    .log-pulse {
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.6; }
        100% { opacity: 1; }
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0d1117 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: rgba(30, 41, 59, 0.5);
        border-radius: 10px 10px 0 0;
        gap: 0;
        padding: 10px 20px;
        color: var(--text-muted);
        border: 1px solid transparent;
        transition: all 0.3s ease;
    }

    .stTabs [aria-selected="true"] {
        background-color: var(--card-bg) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-bottom: none !important;
    }

    /* Global Variable Force */
    :root {
        --st-colors-background: #0f172a !important;
        --st-colors-text: #f8fafc !important;
        --st-colors-primary: #6366f1 !important;
    }

    /* Expander Dark Force - Target all internal elements */
    [data-testid="stExpander"], [data-testid="stExpander"] * {
        background-color: transparent !important;
        color: #f8fafc !important;
    }
    
    [data-testid="stExpander"] {
        background-color: rgba(30, 41, 59, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
    }

    /* File Uploader Browse Button */
    [data-testid="stFileUploader"] button, 
    [data-testid="stFileUploader"] button * {
        background-color: #6366f1 !important;
        color: white !important;
    }

    /* Selectbox Sidebar Force */
    [data-testid="stSidebar"] [data-baseweb="select"],
    [data-testid="stSidebar"] [data-baseweb="select"] * {
        background-color: #1e293b !important;
        color: white !important;
    }

    /* Status Badges */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">Virtual Project Manager</h1>', unsafe_allow_html=True)
st.markdown('<p style="color: #94a3b8; font-size: 1.1rem; margin-top: -15px;">AI-Enabled Strategic Initiation Framework</p>', unsafe_allow_html=True)

with st.sidebar:
    st.header("VPM Control Center")
    provider = st.selectbox("Provider", ["Groq", "Gemini", "Hybrid (Groq+Gemini)"])
    
    # Read from .env only
    final_groq = os.getenv("GROQ_API_KEY")
    final_google = os.getenv("GOOGLE_API_KEY")
    
    st.divider()
    auth_ok = False
    if provider == "Groq":
        auth_ok = bool(final_groq)
    elif provider == "Gemini":
        auth_ok = bool(final_google)
    else:
        auth_ok = bool(final_groq) and bool(final_google)
    
    if auth_ok:
        st.success("System Authenticated via .env")
        st.info("Using keys from environment configuration.")
    else:
        st.error("Authentication Failed")
        st.warning("Please ensure GROQ_API_KEY and GOOGLE_API_KEY are set in your .env file.")

    st.divider()
    st.write("### 🧠 Intelligence Trace")
    if 'vpm_logs' not in st.session_state:
        st.session_state['vpm_logs'] = ["System initialized. Waiting for input..."]
    
    for log in reversed(st.session_state['vpm_logs'][-5:]):
        st.markdown(f'<p class="log-pulse" style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 5px;">🕒 {log}</p>', unsafe_allow_html=True)

    if 'vpm_scope' in st.session_state:
        st.divider()
        st.write("### 📊 Project Maturity")
        gaps = len(st.session_state['vpm_scope'].gap_analysis)
        # Strategic Scoring: Even with gaps, a professional structured core is high maturity
        score = max(50, 100 - (gaps * 3)) # Starts high, drops slowly
        if score > 100: score = 100
        st.progress(score / 100)
        st.write(f"Confidence: **{score}%**")
        if score >= 75:
            st.markdown('<span class="badge" style="background: rgba(34, 197, 94, 0.2); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.4);">Ready for Development</span>', unsafe_allow_html=True)
        elif score >= 40:
            st.markdown('<span class="badge" style="background: rgba(234, 179, 8, 0.2); color: #facc15; border: 1px solid rgba(234, 179, 8, 0.4);">Needs More Detail</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="badge" style="background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.4);">High Risk - Gaps Found</span>', unsafe_allow_html=True)


if not auth_ok:
    st.warning("Please configure API keys to begin.")
else:
    mapped_provider = "groq" if provider == "Groq" else ("gemini" if provider == "Gemini" else "hybrid")
    processor = AIProcessor(provider=mapped_provider, groq_api_key=final_groq, google_api_key=final_google)
    engine = ValidationEngine()

    tab1, tab2, tab3 = st.tabs(["🎯 Project Initiation", "📋 Content Framework", "📚 Knowledge Base"])

    with tab1:
        col_in, col_out = st.columns([1, 1.2])
        
        with col_in:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("### Step 1: Ingest Requirements")
            input_type = st.radio("Source Type", ["Meeting Notes/Emails", "Upload Brief (.docx, .pdf, .xlsx)"])
            
            raw_input = ""
            if input_type == "Meeting Notes/Emails":
                raw_input = st.text_area("Paste discussions or transcripts here:", height=300, placeholder="The client wants a Shopify store with...")
            else:
                uploaded_files = st.file_uploader("Select Documentation", type=["docx", "pdf", "xlsx", "xls"], accept_multiple_files=True, help="Supports .docx, .pdf, and .xlsx formats")
                st.caption("📂 *Supported: Microsoft Word, PDF, and Excel spreadsheets*")
                if uploaded_files:
                    combined_text = []
                    for uploaded_file in uploaded_files:
                        file_ext = uploaded_file.name.split('.')[-1].lower()
                        temp_filename = f"temp_vpm.{file_ext}"
                        with open(temp_filename, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        if file_ext == 'docx':
                            content = read_docx(temp_filename)
                        elif file_ext == 'pdf':
                            content = read_pdf(temp_filename)
                        elif file_ext in ['xlsx', 'xls']:
                            content = read_xlsx(temp_filename)
                        else:
                            content = "Unsupported file type"
                            
                        combined_text.append(f"--- Document: {uploaded_file.name} ---\n{content}")
                        os.remove(temp_filename)
                    raw_input = "\n\n".join(combined_text)
                    st.success(f"{len(uploaded_files)} documents analyzed successfully!")

            if st.button("Generate Strategic Scope"):
                if raw_input:
                    with st.spinner("Analyzing requirements and identifying gaps..."):
                        st.session_state['vpm_logs'].append("Searching Knowledge Base for similar projects...")
                        similar_docs = engine.validate_content(raw_input, n_results=3)
                        context = "\n\n".join(similar_docs)
                        try:
                            st.session_state['vpm_logs'].append(f"Generating Scope using {mapped_provider.upper()}...")
                            scope = processor.generate_scope(raw_input, context)
                            st.session_state['vpm_logs'].append("Scope generated. Performing quality checks...")
                            st.session_state['vpm_scope'] = scope
                            st.session_state['vpm_raw_input'] = raw_input
                            st.session_state['vpm_logs'].append("Strategic Scope finalized.")
                        except Exception as e:
                            st.error(f"Analysis failed: {e}")
                            st.session_state['vpm_logs'].append(f"ERROR: {str(e)}")
                else:
                    st.error("Missing input data.")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_out:
            if 'vpm_scope' in st.session_state:
                scope = st.session_state['vpm_scope']
                st.success(" Strategic Scope Generated")
                
                st.write(f"### {scope.project_title}")
                
                with st.expander("✨ Core Objectives", expanded=True):
                    for obj in scope.objectives:
                        st.markdown(f"- {obj}")
                
                col_scope_a, col_scope_b = st.columns(2)
                with col_scope_a:
                    with st.expander(" In Scope", expanded=True):
                        for item in scope.scope_in:
                            st.markdown(f"- {item}")
                with col_scope_b:
                    with st.expander(" Out of Scope", expanded=True):
                        for item in scope.scope_out:
                            st.markdown(f"- {item}")
                
                st.error(" Gap Analysis (Missing Information)")
                for gap in scope.gap_analysis:
                    st.markdown(f"- {gap}")
                
                with st.expander("💡 Strategic AI Recommendations", expanded=True):
                    for rec in getattr(scope, 'strategic_recommendations', []):
                        st.markdown(f"**🔹 {rec}**")
                
                with st.expander(" Navigation Preview", expanded=False):
                    for n in scope.navigation:
                        st.markdown(f"- {n}")
                
                st.info("🎯 Strategic Scope finalized. Now go to the **'Content Framework'** tab to generate the final interview deliverables.")
                try:
                    qc_scope = check_scope(scope)
                    with st.expander(" Scope Quality Checks", expanded=False):
                        st.write(f"Status: **{qc_scope['status']}**")
                        st.write(f"Terminology Score: {qc_scope['terminology_score']:.2f}")
                        st.write(f"Complete: {qc_scope['complete']}")
                        if qc_scope['issues']:
                            for i in qc_scope['issues']:
                                st.markdown(f"- {i}")
                except Exception as e:
                    st.error(f"Export failed: {e}")
            else:
                st.info("Generated Scope and Gap Analysis will appear here.")

    with tab2:
        if 'vpm_scope' not in st.session_state:
            st.warning("Please generate a Strategic Scope in the 'Project Initiation' tab first.")
        else:
            col_frame_a, col_frame_b = st.columns([1, 1.2])
            
            with col_frame_a:
                st.write("### Step 2: Design Framework")
                st.write("Generate a detailed Sitemap and page-by-page content breakdown based on the approved scope.")
                reference_mode = st.checkbox("Use Reference Mode (exact match if available)")
                if st.button("Generate Content Framework"):
                    st.session_state['vpm_logs'].append("Initiating Content Framework design...")
                    with st.spinner("Designing sitemap and modules..."):
                        try:
                            st.session_state['vpm_logs'].append("Retrieving validation references...")
                            refs = engine.validate_content(st.session_state['vpm_raw_input'], n_results=3)
                            ref_context = "\n\n".join(refs)
                            st.session_state['vpm_logs'].append(f"Processing sitemap with {mapped_provider.upper()}...")
                            framework = processor.generate_framework(st.session_state['vpm_scope'], st.session_state['vpm_raw_input'], ref_context)
                            st.session_state['vpm_framework'] = framework
                            st.session_state['vpm_logs'].append("Visual architecture mapped successfully.")
                            if reference_mode:
                                st.session_state['vpm_logs'].append("Cross-referencing with exact match historical data...")
                                best = engine.find_best_match(st.session_state['vpm_raw_input'])
                                if best and best.get('content'):
                                    st.session_state['vpm_reference_output'] = best['content']
                        except Exception as e:
                            st.error(f"Framework generation failed: {e}")
                            st.session_state['vpm_logs'].append(f"ERROR: {str(e)}")
            
            with col_frame_b:
                if 'vpm_framework' in st.session_state:
                    frame = st.session_state['vpm_framework']
                    st.success(" Content Framework Ready")
                    
                    st.info(f" **CTA Strategy:** {frame.cta_strategy}")

                    st.write("###  Visual Architecture")
                    try:
                        import graphviz
                        dot = graphviz.Digraph(comment='Sitemap')
                        dot.attr(rankdir='LR', size='8,5', bgcolor='transparent')
                        dot.attr('node', shape='rectangle', style='filled,rounded', color='#6366f1', fontcolor='white', fontname='Inter', fontsize='12')
                        dot.attr('edge', color='#94a3b8', arrowhead='vee')
                        
                        root_name = f"Project: {st.session_state['vpm_scope'].project_title}"
                        dot.node('ROOT', root_name, color='#a855f7', shape='doubleoctagon')
                        
                        for i, item in enumerate(frame.header_nav):
                            p_name = safe_get_attr(item, 'main_nav')
                            destination = safe_get_attr(item, 'final_destination')
                            node_id = f"page_{i}"
                            dot.node(node_id, p_name)
                            dot.edge('ROOT', node_id)
                            if destination and destination != p_name:
                                dest_id = f"dest_{i}"
                                dot.node(dest_id, destination)
                                dot.edge(node_id, dest_id)
                            
                        st.graphviz_chart(dot)
                    except Exception as g_err:
                        st.info("Visual architecture graph is preparing...")
                    
                    st.write("### 🗂️ Content Structure")
                    f_tab1, f_tab2, f_tab3 = st.tabs(["Header Nav", "Footer Nav", "Assets"])
                    with f_tab1:
                        st.table([{
                            "Main Nav": safe_get_attr(i, 'main_nav'), 
                            "Dropdown": safe_get_attr(i, 'dropdown'), 
                            "Destination": safe_get_attr(i, 'final_destination'), 
                            "Type": safe_get_attr(i, 'page_type'),
                            "Link": safe_get_attr(i, 'content_link'),
                            "Status": safe_get_attr(i, 'status')
                        } for i in frame.header_nav])
                    with f_tab2:
                        st.table([{
                            "Menu": safe_get_attr(i, 'menu_title'), 
                            "Items": safe_get_attr(i, 'nested_items'), 
                            "Type": safe_get_attr(i, 'page_type'),
                            "Link": safe_get_attr(i, 'content_link'),
                            "Status": safe_get_attr(i, 'status')
                        } for i in frame.footer_nav])
                    with f_tab3:
                        st.table([{
                            "Asset": safe_get_attr(i, 'asset_required'), 
                            "Type": safe_get_attr(i, 'content_type'),
                            "Link": safe_get_attr(i, 'content_link'),
                            "Status": safe_get_attr(i, 'status'),
                            "Notes": safe_get_attr(i, 'client_notes')
                        } for i in frame.website_assets])

                    try:
                        st.write("### 📥 Download")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.download_button("1. Header Navigation", get_header_nav_excel(frame), file_name="header navigation content.xlsx")
                        with col2:
                            st.download_button("2. Footer Navigation", get_footer_nav_excel(frame), file_name="footer navigation content.xlsx")
                        with col3:
                            st.download_button("3. Website Assets", get_website_assets_excel(frame), file_name="website assets.xlsx")
                        
                        st.divider()
                        col_d1, col_d2 = st.columns(2)
                        with col_d1:
                             st.download_button("Download All-in-One Framework", framework_to_excel(frame), file_name="complete_content_framework.xlsx")
                        with col_d2:
                             st.download_button("Download Blank Template (Headers Only)", get_blank_framework_excel(), file_name="blank_content_framework.xlsx")

                            
                        qc_fw = check_framework(frame)
                        with st.expander(" Framework Quality Checks", expanded=False):
                            st.write(f"Status: **{qc_fw['status']}**")
                            st.write(f"Glossary Coverage: {qc_fw['glossary_coverage']:.2f}")
                            st.write(f"Complete: {qc_fw['complete']}")
                            if qc_fw['issues']:
                                for i in qc_fw['issues']:
                                    st.markdown(f"- {i}")
                    except Exception as e:
                        st.error(f"Export failed: {e}")
                    
                    if 'vpm_reference_output' in st.session_state:
                        with st.expander("📎 Reference Output (from Knowledge Base)", expanded=False):
                            st.text_area("Expected Output", st.session_state['vpm_reference_output'], height=300, disabled=True)
                            if st.button("Use Reference as Final Output"):
                                st.session_state['vpm_reference_final'] = True
                                st.success("Reference output selected as final deliverable.")
                            if st.session_state.get('vpm_reference_final'):
                                st.download_button(
                                    "Download Reference Output",
                                    st.session_state['vpm_reference_output'],
                                    file_name="content_framework_reference.txt"
                                )
                    
                    # Feedback Loop simulation
                    st.divider()
                    feedback = st.text_area("Provide Review Comments / Feedback for improvement:")
                    if st.button("Submit Feedback & Update Index"):
                        try:
                            engine.add_feedback(
                                st.session_state['vpm_scope'].json(),
                                st.session_state['vpm_framework'].json(),
                                feedback
                            )
                            st.success("Feedback captured and added to Knowledge Base.")
                        except Exception as e:
                            st.error(f"Feedback processing failed: {e}")
                else:
                    st.info("Content Framework detailing navigation and page modules will appear here.")
                    st.download_button("Download Blank Template (Headers Only)", get_blank_framework_excel(), file_name="blank_content_framework.xlsx")

    with tab3:
        st.write("### 📚 Strategic Knowledge Base & Exact Export")
        st.write("Select an example to download the exact Output files as an All-in-One Frame.")
        try:
            data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
            examples = get_example_paths(data_dir)
            names = [ex['name'] for ex in examples]
            if names:
                name = st.selectbox("Example", names)
                selected = next(ex for ex in examples if ex['name'] == name)
                input_files = selected['input_files']
                output_files = selected['output_files']
                with st.expander("📄 Inputs", expanded=False):
                    for f in input_files:
                        st.markdown(f"- {os.path.basename(f)}")
                import io, zipfile
                def make_zip(paths):
                    bio = io.BytesIO()
                    with zipfile.ZipFile(bio, 'w', zipfile.ZIP_DEFLATED) as z:
                        for p in paths:
                            if os.path.isfile(p):
                                z.write(p, arcname=os.path.basename(p))
                    bio.seek(0)
                    return bio.getvalue()
                if output_files:
                    zip_bytes = make_zip(output_files)
                    st.download_button("Download All-in-One Frame (Exact Output ZIP)", zip_bytes, file_name=f"{name}_Output.zip")
                else:
                    st.info("No output files found for this example.")
            else:
                st.info("No examples found in data folder.")
        except Exception as e:
            st.error(f"Error: {e}")
