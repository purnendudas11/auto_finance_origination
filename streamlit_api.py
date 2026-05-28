from dotenv import load_dotenv
import json
import logging
import logging.config
import os
import requests
import streamlit as st
import uuid
import yaml

load_dotenv()

# Configure logging using YAML
if os.path.exists("logging.yaml"):
    with open("logging.yaml", "r") as file:
        config = yaml.safe_load(file)
        logging.config.dictConfig(config)
else:
    log_level = logging.getLevelNamesMapping()[(os.environ.get("LOG_LEVEL", "INFO"))]
    logging.basicConfig(level=log_level)

logger = logging.getLogger(__name__)

# Fallback Configuration mapping
API_URL = "https://2nxvlqfeoa.execute-api.us-east-1.amazonaws.com/dev/origination"
ui_title = os.environ.get("BEDROCK_AGENT_TEST_UI_TITLE", "Welcome to SmartBuddy - Your Auto Finance Origination Agent")
ui_icon = os.environ.get("BEDROCK_AGENT_TEST_UI_ICON", "🚗")

# --- STEP 1: INITIALIZE STREAMLIT STATE AT THE TOP ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

def init_session_state():
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []

# General page configuration
st.set_page_config(page_title=ui_title, page_icon=ui_icon, layout="wide")
st.title(ui_title)

# --- STEP 2: SINGLE CONSOLIDATED SIDEBAR BLOCK ---
# with st.sidebar:
#     st.header("Session Settings")
#     if st.button("Reset Session"):
#         init_session_state()
#         st.rerun()
#     st.divider()
#     st.caption(f"**Active Session Context:** {st.session_state.session_id}")
#     st.caption(f"**Target URL:** {API_URL}")

# --- STEP 3: RENDER HISTORICAL CHAT UI ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)

# --- STEP 4: INTERCEPT INPUT AND MAKE THE POST CALL ---
if prompt := st.chat_input("Ask your question here..."):
    # 1. Append user prompt immediately to UI state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Open assistant rendering block with spinner loader
    with st.chat_message("assistant"):
        with st.spinner("Processing request..."):
            
            payload = {
                "session_id": st.session_state.session_id,
                "prompt": prompt
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            logger.info(f"Firing API Request to: {API_URL}")
            logger.info(f"Payload sent: {json.dumps(payload)}")
            
            try:
                # 3. Explicitly execute the network POST command
                response = requests.post(
                    API_URL,
                    json=payload,
                    headers=headers,
                    timeout=45  # Generous threshold for cloud Lambda cold-starts
                )
                
                logger.info(f"API HTTP Status Code response: {response.status_code}")
                
                if response.status_code == 200:
                    raw_text = response.text
                    logger.info(f"Raw backend text payload: {raw_text}")
                    
                    if not raw_text.strip():
                        output_text = "⚠️ Success status received, but backend returned an empty string response."
                    else:
                        try:
                            # Layer 1: Parse the top-level string (Extracts statusCode, headers, body)
                            initial_data = response.json()
                            
                            # Extract the body contents
                            body_content = initial_data.get("body") if isinstance(initial_data, dict) else initial_data
                            
                            # Layer 2: If the body is still a text string, parse it again into a Python dictionary
                            if isinstance(body_content, str):
                                try:
                                    body_content = json.loads(body_content)
                                except json.JSONDecodeError:
                                    pass # Keep it as a string if it's already raw text
                            
                            # Layer 3: Recursively dig through the un-wrapped inner dictionary keys
                            while isinstance(body_content, dict):
                                if "result" in body_content:
                                    body_content = body_content["result"]
                                elif "response" in body_content:
                                    body_content = body_content["response"]
                                elif "text" in body_content:
                                    body_content = body_content["text"]
                                else:
                                    break
                            
                            # Final Type Check: Format output cleanly
                            if isinstance(body_content, str):
                                output_text = body_content
                            else:
                                output_text = json.dumps(body_content)
                                
                        except json.JSONDecodeError:
                            output_text = raw_text
                else:
                    output_text = f"⚠️ API Error: Server returned response code `{response.status_code}`."
                    logger.error(f"Error payload: {response.text}")

                    
            except requests.exceptions.Timeout:
                output_text = "⚠️ Network Timeout. The cloud backend took too long to return a string."
                logger.error("POST call hit timeout limits.")
            except requests.exceptions.ConnectionError:
                output_text = "⚠️ Network Connection Error. Unable to establish connection to the AWS Gateway endpoint."
                logger.error("Failed to route out of local network to destination API.")
            except Exception as e:
                output_text = f"⚠️ Unexpected script processing error: `{str(e)}`"
                logger.error(f"Script breakdown: {str(e)}")

            # 4. Save engine output to UI array and print on screen
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            st.markdown(output_text, unsafe_allow_html=True)
