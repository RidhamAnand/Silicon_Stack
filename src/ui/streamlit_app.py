"""Minimal Streamlit chat UI for Silicon Stack

This is a lightweight, minimalist chat interface that defers heavy backend imports
until the user sends a message. It aims to be robust when some ML dependencies
are missing by showing helpful errors and allowing explicit escalation (ticket)
creation using the `escalation_agent` which has lighter runtime deps.

Run with:
    streamlit run src/ui/streamlit_app.py
"""
from __future__ import annotations
import streamlit as st
from typing import List, Dict
from datetime import datetime

st.set_page_config(page_title="Silicon Stack — Support", layout="wide")


def _css():
    # Modern, minimalist styling inspired by contemporary chat UIs
    st.markdown(
        """
        <style>
        :root{
          --bg: #0f172a;
          --card: #0b1220;
          --accent: #7c3aed;
          --muted: #9ca3af;
          --user-bg: #0550a6;
          --assistant-bg: #111827;
        }
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    body { background: linear-gradient(180deg,#0b1220 0%, #07192b 100%); font-family: 'Inter', sans-serif; }
    .app-title { font-weight:800; color: #ffffff; font-size:20px; }
    .subtitle { color: var(--muted); margin-top: -6px; font-size:13px }
    .chat-window { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); padding:18px; border-radius:14px; height:68vh; overflow:auto; box-shadow: 0 6px 30px rgba(2,6,23,0.6); }
    .bubble { max-width:78%; padding:12px 16px; border-radius:14px; margin:10px 0; display:inline-block; font-size:15px; line-height:1.45; white-space:pre-wrap; }
    .bubble.user { background: linear-gradient(90deg, #0366d6, #0550a6); color: #fff; border-bottom-right-radius:6px; box-shadow: 0 6px 18px rgba(3,102,214,0.18); }
    .bubble.assistant { background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01)); color:#e6eef8; border-bottom-left-radius:6px; box-shadow: 0 6px 18px rgba(2,6,23,0.3); }
        .meta { color: var(--muted); font-size:12px; margin-top:4px; }
        .header { display:flex; align-items:center; gap:12px; padding:12px 0; }
        .brand { background: linear-gradient(90deg,#7c3aed,#06b6d4); padding:8px 12px; border-radius:10px; color:white; font-weight:700; }
        .sidebar-card { background: rgba(255,255,255,0.02); padding:12px; border-radius:10px; }
        .accent-btn { background: linear-gradient(90deg,#7c3aed,#06b6d4); color: white; padding:8px 12px; border-radius:8px; border:none; }
    .avatar { width:36px; height:36px; border-radius:50%; display:inline-block; text-align:center; line-height:36px; font-weight:700; color:white; }
    .avatar.user { background: linear-gradient(90deg,#06b6d4,#7c3aed); }
    .avatar.assistant { background: #0b1220; border: 1px solid rgba(255,255,255,0.04); }
    .footer { color: var(--muted); font-size:12px; margin-top:8px }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []  # List[Dict(role, content, ts)]
    if 'session_id' not in st.session_state:
        st.session_state.session_id = f"session_{int(datetime.utcnow().timestamp())}"
    if 'db_connected' not in st.session_state:
        st.session_state.db_connected = False


def append_message(role: str, content: str):
    st.session_state.messages.append({
        'role': role,
        'content': content,
        'ts': datetime.utcnow().isoformat()
    })


def render_messages():
    # Render messages with modern bubbles + small avatars
    for msg in st.session_state.messages:
        role = msg['role']
        content = msg['content']
        ts = msg.get('ts', '')
        # Safe HTML: escape content for HTML insertion
        safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        if role == 'user':
            st.markdown(f"<div style='display:flex; justify-content:flex-end; gap:8px; align-items:flex-end;'><div class='meta' style='margin-right:8px'>{ts}</div><div class='bubble user'>{safe_content}</div><div class='avatar user'>Y</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='display:flex; justify-content:flex-start; gap:12px; align-items:flex-start;'><div class='avatar assistant'>S</div><div class='bubble assistant'>{safe_content}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='display:flex; justify-content:flex-start; margin-top:2px;'><div class='meta'>{ts}</div></div>", unsafe_allow_html=True)


def get_backend_reply(user_query: str, session_id: str) -> Dict:
    """Try to query the full backend pipeline. If it fails (heavy deps), return an error
    along with a friendly message and a flag indicating failure.
    """
    try:
        # Import lazily to avoid heavy imports at app startup
        from src.rag.pipeline import rag_pipeline
        # The project's rag pipeline exposes a `query` method similar to the CLI
        result = rag_pipeline.query(user_query, include_sources=False, conversation_context=None)
        return { 'ok': True, 'response': result.get('response', 'No response from pipeline'), 'meta': result }
    except Exception as e:
        # Fallback: try lightweight router or escalation agent import
        try:
            from src.agents.router_agent import router_agent
            # Use router to at least make a routing decision (no full response)
            routing = router_agent.route_query(session_id, user_query)
            return { 'ok': False, 'response': f"(Routing only) Routed to: {routing['routing_decision']['target_agent']}", 'error': str(e) }
        except Exception:
            # Last resort: return a simple friendly error
            return { 'ok': False, 'response': "Backend unavailable (heavy ML deps). You can still create an escalation ticket.", 'error': str(e) }


def try_create_escalation(chat_history: List[Dict], user_query: str) -> Dict:
    """Call the EscalationAgent handle_escalation using chat history. This avoids importing
    heavy embedding/transformers libs and lets users open tickets even if the full
    pipeline is not functional.
    """
    try:
        from src.agents.escalation_agent import escalation_agent
        result = escalation_agent.handle_escalation(chat_history=chat_history, user_query=user_query, interactive=False)
        return result
    except Exception as e:
        return { 'success': False, 'message': f'Failed to call escalation agent: {e}' }


def main():
    _css()
    init_state()

    st.title("Silicon Stack — Support Chat")
    st.write("A minimalist chat UI to interact with the support assistant.")

    col1, col2 = st.columns([3,1])

    with col1:
        st.subheader("Conversation")
        render_messages()

    with col2:
        st.subheader("Actions")
        st.write("Session:", st.session_state.session_id)
        if st.button("Clear chat"):
            st.session_state.messages = []

    st.markdown("---")

    with st.form(key='input_form', clear_on_submit=False):
        user_input = st.text_input("Your message", key='user_input')
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        append_message('user', user_input)
        # Prepare chat_history as simple list of dicts
        chat_history = [{'role': m['role'], 'content': m['content']} for m in st.session_state.messages]

        backend_result = get_backend_reply(user_input, st.session_state.session_id)

        if backend_result.get('ok'):
            assistant_text = backend_result.get('response')
            append_message('assistant', assistant_text)
        else:
            # Show fallback response and offer escalation
            assistant_text = backend_result.get('response')
            append_message('assistant', assistant_text)
            st.warning('Note: full backend may be unavailable. You can still create an escalation ticket.')

    st.markdown("---")

    st.subheader("Quick Escalation")
    st.write("If you'd like to open a support ticket based on the conversation above, click below.")
    if st.button("Create Escalation Ticket"):
        chat_history = [{'role': m['role'], 'content': m['content']} for m in st.session_state.messages]
        last_user = next((m['content'] for m in reversed(st.session_state.messages) if m['role']=='user'), '')
        res = try_create_escalation(chat_history, last_user)
        if res.get('success'):
            msg = f"Ticket created: {res.get('ticket_id')} — {res.get('message')}"
            append_message('assistant', msg)
            st.success(msg)
        else:
            err = res.get('message') or res.get('details') or 'Unknown error'
            append_message('assistant', f"Failed to create ticket: {err}")
            st.error(f"Failed to create ticket: {err}")

        st.markdown("---")

        # View tickets by email and show all tickets
        st.markdown("### My Tickets")
        email_q = st.text_input("Enter your email to view tickets", key='tickets_email')
        if st.button("Show my tickets") and email_q:
            try:
                from src.database.service import db_service
                if not db_service.is_connected():
                    db_service.connect()
                # Try to use DB-backed summary if available
                summary = None
                try:
                    tickets_col = db_service.client.get_collection('tickets')
                    docs = list(tickets_col.find({"user_email": email_q}).sort('created_at', -1).limit(50))
                    summary = {
                        'total': len(docs),
                        'tickets': [
                            {
                                '_id': str(d.get('_id')) if d.get('_id') else None,
                                'ticket_id': d.get('ticket_id'),
                                'title': d.get('title'),
                                'status': d.get('status'),
                                'priority': d.get('priority'),
                                'user_email': d.get('user_email'),
                                'order_number': d.get('order_number'),
                                'created_at': d.get('created_at')
                            }
                            for d in docs
                        ]
                    }
                except Exception:
                    # Fallback to in-memory ticket manager
                    from src.tickets.ticket_manager import ticket_manager
                    summary = ticket_manager.get_tickets_summary(email_q)

                st.json(summary)
            except Exception as e:
                st.error(f"Failed to fetch tickets: {e}")

        if st.button("Show all tickets"):
            try:
                from src.database.service import db_service
                if not db_service.is_connected():
                    ok = db_service.connect()
                    if not ok:
                        st.error("DB connection failed; cannot list tickets")
                        raise RuntimeError("DB connect failed")

                tickets_col = db_service.client.get_collection('tickets')
                docs = list(tickets_col.find({}).sort('created_at', -1).limit(200))

                # Normalize docs for display
                rows = []
                for d in docs:
                    rows.append({
                        '_id': str(d.get('_id')) if d.get('_id') else None,
                        'ticket_id': d.get('ticket_id'),
                        'title': d.get('title'),
                        'status': d.get('status'),
                        'priority': d.get('priority'),
                        'user_email': d.get('user_email'),
                        'order_number': d.get('order_number'),
                        'created_at': d.get('created_at')
                    })

                with st.expander(f"All tickets ({len(rows)})", expanded=True):
                    if rows:
                        st.dataframe(rows)
                    else:
                        st.info("No tickets found in the database.")

            except Exception as e:
                st.error(f"Failed to list tickets: {e}")

if __name__ == '__main__':
    main()
