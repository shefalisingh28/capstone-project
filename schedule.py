
import streamlit as st
import google.generativeai as genai
import json
import os

# ==========================================
# 1. SETUP & CONFIGURATION
# ==========================================
st.set_page_config(page_title="AI Scheduler Capstone", page_icon="📅", layout="wide")

# 👇👇 I HAVE PUT YOUR KEY HERE FOR YOU 👇👇
API_KEY = "api"
# 👆👆 DO NOT CHANGE THIS LINE 👆👆

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error(f"API Key Error: {e}")

# ==========================================
# 2. THE AI AGENT CLASS
# ==========================================
class ScheduleAgent:
    def __init__(self):
        # Using the specific '001' version to fix the 404 error
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_schedule(self, user_profile, tasks, unexpected_event=None):
        prompt = f"""
        You are an elite Productivity AI Agent.
        
        USER PROFILE: {json.dumps(user_profile)}
        TASKS: {json.dumps(tasks)}
        
        CONTEXT CHANGE:
        {f"The user reported this issue: {unexpected_event}. RECALCULATE the schedule." if unexpected_event else "Create a fresh optimized schedule."}

        OUTPUT FORMAT:
        Return ONLY valid JSON array. No markdown.
        [
            {{ "time": "HH:MM - HH:MM", "activity": "Task Name", "reason": "Short logic", "type": "Work/Break/Chore" }}
        ]
        """
        try:
            response = self.model.generate_content(prompt)
            clean_text = response.text.strip()
            
            # Fix JSON formatting issues
            if clean_text.startswith("```json"):
                clean_text = clean_text.replace("```json", "").replace("```", "")
            elif clean_text.startswith("```"):
                clean_text = clean_text.replace("```", "")
                
            return json.loads(clean_text)
        except Exception as e:
            st.error(f"AI Generation Error: {e}")
            return []

# ==========================================
# 3. STREAMLIT UI
# ==========================================
st.title("🤖 AI Autonomous Scheduler")
st.markdown("### Capstone Project: Dynamic Agentic Workflow")

agent = ScheduleAgent()
if 'schedule' not in st.session_state:
    st.session_state.schedule = None

col1, col2 = st.columns(2)

# --- LEFT COLUMN: INPUTS ---
with col1:
    st.subheader("1. User Profile & Tasks")
    default_tasks = [
        {"task": "Capstone Coding", "duration": "2 hours", "priority": "High"},
        {"task": "Laundry", "duration": "30 mins", "priority": "Low"},
        {"task": "Team Meeting", "fixed_time": "14:00", "duration": "1 hour"}
    ]
    st.json(default_tasks, expanded=False)
    
    if st.button("🚀 Generate Initial Schedule"):
        with st.spinner("AI is thinking..."):
            user_profile = {"energy_peak": "Morning", "start": "09:00"}
            st.session_state.schedule = agent.generate_schedule(user_profile, default_tasks)
            st.success("Schedule Generated!")

# --- RIGHT COLUMN: OUTPUTS ---
with col2:
    st.subheader("2. Your Optimized Day")
    
    if st.session_state.schedule:
        for slot in st.session_state.schedule:
            emoji = "📝"
            if "Break" in slot.get('activity', ''): emoji = "☕"
            elif "Meeting" in slot.get('activity', ''): emoji = "👥"
            
            with st.expander(f"{emoji} {slot['time']} : {slot['activity']}", expanded=True):
                st.write(f"**Why:** {slot['reason']}")
    else:
        st.info("No schedule generated yet.")

# --- BOTTOM SECTION: DISRUPTION ---
st.markdown("---")
st.subheader("3. Simulate Unexpected Event (Agentic Adaptation)")

disruption = st.text_input("What happened?", placeholder="Example: I overslept until 11am")

if st.button("🔄 Re-Calculate Schedule"):
    if st.session_state.schedule and disruption:
        with st.spinner("Agent is negotiating tasks..."):
            user_profile = {"energy_peak": "Morning", "start": "09:00"}
            st.session_state.schedule = agent.generate_schedule(
                user_profile, default_tasks, unexpected_event=disruption
            )
            st.rerun()
