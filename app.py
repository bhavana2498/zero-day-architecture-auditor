import os
import streamlit as st
from dotenv import load_dotenv
from google import genai
from PIL import Image

# Load the secret API key
load_dotenv()

def fetch_latest_threat_intel():
    """Simulates a Cloud Threat Intelligence feed."""
    cloud_threats = [
        "- **CVE-2024-21626 (Container Breakout)**: Vulnerability in runc allowing attackers to escape container isolation.",
        "- **CVE-2023-47627 (Cloud Data Exposure)**: Misconfigured default permissions in AWS S3 or Azure Blob storage.",
        "- **CVE-2023-34362 (Unauthenticated RCE)**: Remote Code Execution flaw targeting internet-facing web applications.",
        "- **Identity Threat (IAM Privilege Escalation)**: Over-provisioned wildcard (*) permissions in cloud roles.",
        "- **Cleartext Transit (Zero-Trust Violation)**: Traffic between internal subnets moving over unencrypted HTTP."
    ]
    return "Latest Cloud Threat Intelligence:\n" + "\n".join(cloud_threats)

def analyze_architecture(img, threat_intel):
    """Sends the image and threat intel to Gemini Flash for analysis."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return "Error: GEMINI_API_KEY not found. Please check your .env file."
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    Act as a Principal Cloud Security Architect. I am providing an image of a cloud infrastructure diagram.
    
    Here is the live threat intelligence for this week:
    {threat_intel}
    
    Perform a strict Threat Model analysis:
    1. Identify the components visible in this diagram.
    2. Point out exactly where this architecture fails security best practices, referencing the provided threat intel where applicable.
    3. Output the exact, production-ready Terraform code required to secure the top 2 critical vulnerabilities you found.
    
    Format your entire response in clean Markdown. Do not include pleasantries.
    """

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[img, prompt]
        )
        return response.text
    except Exception as e:
        return f"Gemini API Error: {e}"

# --- STREAMLIT UI ---
st.set_page_config(page_title="Zero-Day Architecture Auditor", layout="wide")

st.title("🛡️ Zero-Day Architecture Auditor")
st.markdown("Upload a cloud architecture diagram. The AI will visually parse the infrastructure, cross-reference it with live threat intel, and generate Terraform code to patch vulnerabilities.")

# 1. Fetch the intel and display it in a clean sidebar
intel = fetch_latest_threat_intel()
with st.sidebar:
    st.header("🔴 Live Threat Intel")
    st.markdown(intel)
    st.info("The AI uses this context to prioritize its security audit.")

# 2. File uploader for the diagram
uploaded_file = st.file_uploader("Upload Architecture Diagram (PNG/JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Display the uploaded image
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Architecture Diagram", use_container_width=True)
    
    # 3. The "Run" button
    if st.button("Run Security Audit & Generate Terraform", type="primary"):
        with st.spinner("Analyzing architecture topology and cross-referencing CVEs..."):
            result = analyze_architecture(img, intel)
            
            st.success("Audit Complete!")
            st.markdown("### Security Report & Remediation Code")
            st.markdown(result)

# --- Footer Disclaimer ---
st.divider()
st.caption("🛡️ **Zero-Day Architecture Auditor **")
st.warning("""
**DISCLAIMER:**
- **For Educational Purposes Only:** This application is a proof-of-concept developed for a professional portfolio to demonstrate AI integration in DevSecOps workflows.
- **Not for Production:** This code should not be used to secure live enterprise environments.
- **Validation Required:** All AI-generated Terraform outputs must be manually audited by a certified Cloud Architect.
""")