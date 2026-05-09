import logging
from typing import Optional, Sequence

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.core.config import GROQ_API_KEY, MODEL_NAME
from app.services.prompt import SYSTEM_PROMPT
from app.tools.availibility import check_availability_by_specialization
from app.tools.patient_tool  import get_or_create_patient_tool
from app.tools.appointment_booking  import book_appointment_tool
from app.tools.email_tool        import send_confirmation_email_tool

logger = logging.getLogger(__name__)

# ── Tools ─────────────────────────────────────────────────────────
CHAT_TOOLS = [
    check_availability_by_specialization,
    get_or_create_patient_tool,
    book_appointment_tool,
    send_confirmation_email_tool,
]

# ── LLM — Groq ────────────────────────────────────────────────────
_llm = ChatGroq(
    model_name    = MODEL_NAME,
    groq_api_key  = GROQ_API_KEY,
    temperature   = 0,
    streaming     = False,
)

# ── Prompt ────────────────────────────────────────────────────────
_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    MessagesPlaceholder("chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

# ── Agent ─────────────────────────────────────────────────────────
_agent = create_tool_calling_agent(_llm, CHAT_TOOLS, _prompt)

_executor = AgentExecutor(
    agent=_agent,
    tools=CHAT_TOOLS,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True,
    return_intermediate_steps=True,
)


# ── Main Function ─────────────────────────────────────────────────
def run_chat_turn(
    user_message: str,
    chat_history: Optional[Sequence[BaseMessage]] = None,
    patient_id:   Optional[str] = None,
) -> str:

    if not user_message or not user_message.strip():
        return "I didn't receive your message. Could you please try again?"

    # ── Inject patient_id if already known ────────────────────────
    enriched_input = user_message
    if patient_id:
        enriched_input = (
            f"{user_message}\n"
            f"[System note: patient_id is already known: {patient_id}]"
        )

    history = list(chat_history) if chat_history else []

    logger.info(
        f"Chat turn | patient_id={patient_id} | "
        f"history={len(history)} msgs | "
        f"message={user_message[:50]}"
    )

    try:
        result = _executor.invoke({
            "input":        enriched_input,
            "chat_history": history,
        })

        reply = (result.get("output") or "").strip()

        # ── Log tool calls ────────────────────────────────────────
        steps = result.get("intermediate_steps", [])
        for step in steps:
            if step and len(step) >= 1:
                action = step[0]
                logger.info(
                    f"Tool called: {getattr(action, 'tool', 'unknown')} | "
                    f"Input: {getattr(action, 'tool_input', {})}"
                )

        if not reply:
            return "I could not produce a response. Please try again."

        logger.info(f"Agent reply: {reply[:100]}")
        return reply

    # ── Groq specific error ───────────────────────────────────────
    except Exception as e:
        error_str = str(e).lower()

        # Groq bad request — usually tool calling format issue
        if "bad request" in error_str or "400" in error_str:
            logger.warning(f"Groq bad request: {str(e)}")
            return (
                "I could not process that request. "
                "Could you rephrase and mention the doctor type clearly?"
            )

        # Rate limit
        if "rate limit" in error_str or "429" in error_str:
            logger.warning("Groq rate limit hit")
            return (
                "I am receiving too many requests right now. "
                "Please try again in a moment."
            )

        # Context too long
        if "context" in error_str or "tokens" in error_str:
            logger.warning("Groq context length exceeded")
            return (
                "Our conversation is getting long. "
                "Let me start fresh — how can I help you today?"
            )

        logger.error(f"Agent error: {str(e)}")
        return (
            "I'm sorry, something went wrong. "
            "Please try again or call us directly at the clinic."
        )