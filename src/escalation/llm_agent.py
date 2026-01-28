"""LLM escalation agent for borderline/high-impact emails.

Per contract scanner-api.md §4 and research.md R2.
Uses Gemini client via agents framework as specified.
"""

import os
from typing import TYPE_CHECKING

from src.models.scan_result import LLMReviewResult
from src.models.signal import Signal


class LLMUnavailableError(Exception):
    """Raised when LLM service cannot be reached."""
    pass


async def escalate(
    email_text: str,
    sender: str,
    risk_score: int,
    classification: str,
    signals: list[Signal],
) -> LLMReviewResult:
    """Invoke LLM agent for secondary review of borderline/high-impact email.

    Args:
        email_text: Raw email text (truncated to first 2000 chars for LLM).
        sender: Sender identifier.
        risk_score: ML-produced score (read-only, not modifiable).
        classification: ML-determined classification.
        signals: Top contributing signals from ML model.

    Returns:
        LLMReviewResult with explanation, optional label suggestion,
        rationale referencing ML signals, and full prompt/response logs.

    Raises:
        LLMUnavailableError: If LLM service cannot be reached.
            Caller must handle fallback to ML-only explanation.
    """
    # Import the openai-agents framework and dotenv
    try:
        from agents.agent import Agent
        from agents.run import Runner, RunConfig
        from agents.models.openai_chatcompletions import OpenAIChatCompletionsModel
        from openai import AsyncOpenAI
        from dotenv import load_dotenv, find_dotenv
    except ImportError:
        raise LLMUnavailableError("openai-agents or python-dotenv package not installed")

    # Load environment variables
    load_dotenv(find_dotenv())

    # Validate API key is available
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise LLMUnavailableError("GEMINI_API_KEY environment variable not set")

    # Truncate email to prevent token limits
    truncated_email = email_text[:2000]

    # Format signals for LLM consumption
    signal_descriptions = []
    for signal in signals[:5]:  # Top 5 signals
        if signal.value:
            signal_descriptions.append(f"- {signal.display_name}: {signal.value}")

    # Construct prompt per research.md R5 (template-based approach with LLM augmentation)
    prompt = f"""You are a security expert reviewing an email that has been flagged by an ML classifier.
Provide a careful assessment focusing on phishing indicators.

EMAIL CONTENT:
From: {sender}
Body: {truncated_email}

ML CLASSIFIER OUTPUT:
- Risk Score: {risk_score}/100
- Classification: {classification}
- Top Contributing Signals:
{chr(10).join(signal_descriptions)}

Please provide:
1. A brief explanation of whether this email appears legitimate or suspicious
2. Any specific phishing indicators you notice
3. Whether you agree with the ML classification or suggest a different one
4. Specific recommendations for the recipient

Keep your response concise but thorough. Focus on the content, sender authenticity,
and potential social engineering tactics."""

    # 0.1. Loading the environment variables (as per your example)
    load_dotenv(find_dotenv())

    # 1. Which LLM Provider to use? -> Google Chat Completions API Service
    external_client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    # 2. Which LLM Model to use?
    llm_model = OpenAIChatCompletionsModel(
        model=os.getenv("SCANNER_LLM_MODEL", "gemini-2.5-flash"),
        openai_client=external_client
    )

    # 3. Creating the Agent
    agent = Agent(name="SecurityAssistant", model=llm_model)

    # 4. Running the Agent with tracing disabled
    run_config = RunConfig(
        model=llm_model,
        model_provider=external_client,
        tracing_disabled=True,
    )

    try:
        result = await Runner.run(
            starting_agent=agent,
            input=prompt,
            run_config=run_config,
        )
        llm_response = result.final_output

        # FR-006: LLM MUST NOT change the ML risk score value
        # We return the LLM's assessment but preserve the original score
        return LLMReviewResult(
            llm_explanation=llm_response,
            suggested_label=None,  # LLM can suggest but we don't change the score
            rationale=f"LLM reviewed email with ML risk score {risk_score} and provided additional analysis.",
            prompt_log=prompt,
            response_log=llm_response
        )
    except Exception as e:
        raise LLMUnavailableError(f"Failed to call LLM service: {str(e)}")
