# =============================================================
# AI COUNCIL v5.0 — Non-Redundant, Domain-Aware, Streaming Experts
# Includes: expert personality enforcement, memory-aware prompts,
#           verdict synthesis, token cap per expert, council summary
# =============================================================

from Everything_else.model_registry import load_model_from_config, get_stop_sequence

# User-facing names for expert display
PRETTY_NAMES = {
    "jynx_summarizer": "Summary",
    "jynx_expert_logic": "Logic Expert",
    "jynx_expert_math": "Math Expert",
    "jynx_expert_coding": "Coding Expert",
    "jynx_expert_emotion": "Emotion Expert",
    "jynx_expert_survival": "Survival Expert",
    "jynx_expert_finance": "Finance Expert",
    "jynx_expert_psychology": "Psychology Expert",
    "jynx_expert_medical": "Medical Expert",
    "jynx_expert_cyber": "Cybersecurity Expert",
    "jynx_judge": "Final Verdict",
    "jynx_expert_history": "History Expert",
    "jynx_expert_sarcasm": "People Expert",
    "jynx_expert_politics": "Political Expert",
    "jynx_expert_conspiracy": "Conspiracy Intelligence Expert",
    "jynx_expert_mental_health": "Mental Health Expert",
}

# Maps domain keyword to model ID
EXPERT_MAP = {
    "logic": "jynx_expert_logic",
    "math": "jynx_expert_math",
    "coding": "jynx_expert_coding",
    "emotion": "jynx_expert_emotion",
    "survival": "jynx_expert_survival",
    "finance": "jynx_expert_finance",
    "psychology": "jynx_expert_psychology",
    "medical": "jynx_expert_medical",
    "cyber": "jynx_expert_cyber",
    "history": "jynx_expert_history",
    "people": "jynx_expert_sarcasm",
    "politics": "jynx_expert_politics",
    "conspiracy": "jynx_expert_conspiracy",
    "mental health": "jynx_expert_mental_health",
}

# Short domain descriptions for personality reinforcement
FIELD_DESCRIPTIONS = {
    "jynx_expert_logic": "logical decision-making and structured analysis",
    "jynx_expert_math": "mathematics and abstract numerical reasoning",
    "jynx_expert_coding": "software development, code, and technical systems",
    "jynx_expert_emotion": "emotional intelligence and inner feelings",
    "jynx_expert_survival": "practical off-grid skills, survival, and physical strategy",
    "jynx_expert_finance": "personal finance, economics, and money management",
    "jynx_expert_psychology": "mental health, motivation, and behavior",
    "jynx_expert_medical": "physical health, medicine, and biology",
    "jynx_expert_cyber": "cybersecurity, digital systems, and network thinking",
    "jynx_expert_history": "history and strategic military stratey",
    "jynx_expert_sarcasm": "people, motivations, fears, risks, and human nature",
    "jynx_expert_politics": "political power, shady business dealings, and extortion",
    "jynx_expert_conspiracy": "conspiracy theories, intelligence agencies, and criminal networks",
    "jynx_expert_mental_health": "therapy techniques, emotional intelligence, and self-help",
}

# Sequence enforced for deterministic council order
DEFAULT_SEQUENCE = [
    "emotion", "psychology", "survival", "finance"
]


# =============================================================
# COUNCIL ENTRY POINT — STREAMING LOGIC
# =============================================================
def run_council_streaming(user_prompt):
    # === 1. SUMMARIZER STEP ===
    summarizer_prompt = f"""
You are the AI Council Summarizer.

Your job:
1. Summarize the user's request in one clear sentence.
2. Choose 5 experts to respond ONLY from this list: Logic, Math, Coding, Emotion, Survival, Finance, Psychology, Medical, Cyber, History, People, Politics, Mental Health, and Conspiracy.
3. Output EXACTLY:

**Task Summary:** <one sentence>
**Experts:** <comma-separated list>

User prompt:
{user_prompt.strip()}

Do not repeat the user prompt or create more than 1 task summary.
"""
    llm_fn, scfg = load_model_from_config("jynx_summarizer")
    summary_buffer = ""

    for chunk in llm_fn(
        summarizer_prompt,
        stream_override=True,
        max_tokens=scfg.get("max_tokens", 200),
        temperature=scfg.get("temperature", 0.7),
        stop=get_stop_sequence("jynx_summarizer"),
    ):
        token = chunk.get("choices", [{}])[0].get("text") or \
                chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
        if token:
            summary_buffer += token
            yield ("summary", token)

    yield ("summary_done", summary_buffer)

    # === 2. DETERMINE EXPERTS ===
    lower = summary_buffer.lower()
    mentioned = [k for k in EXPERT_MAP if k in lower]
    expert_ids = [EXPERT_MAP[k] for k in mentioned] or ["jynx_expert_logic"]
    expert_ids = expert_ids[:4]  # Cap max experts

    # === 3. EXPERT RESPONSES ===
    previous_notes = ""

    for expert_id in expert_ids:
        expert_name = PRETTY_NAMES.get(expert_id, expert_id)
        field = FIELD_DESCRIPTIONS.get(expert_id, "your area of expertise")
        yield ("expert_start", expert_name)

        expert_prompt = f"""
You are the {expert_name}, a strict domain expert in {field}.

Your Job:
- Respond in 2-3 paragraphs with actionable steps.
- Do NOT repeat the prompt or give yourself instructions.


User prompt:
{user_prompt}

Earlier experts:
{previous_notes or "None yet."}

- Refer to others by name and introduce a new perspective based on your expertise.
- Find a way to challenge earlier views.
- ONLY discuss your expertise

Your Response:
"""
        llm_fn, ecfg = load_model_from_config(expert_id)
        expert_buffer = ""
        token_count = 0
        token_limit = ecfg.get("generation_token_limit", 400)

        for chunk in llm_fn(
            expert_prompt,
            stream_override=True,
            max_tokens=ecfg.get("max_tokens", 2048),
            temperature=ecfg.get("temperature", 0.7),
            stop=get_stop_sequence(expert_id),
        ):
            token = chunk.get("choices", [{}])[0].get("text") or \
                    chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
            if token:
                expert_buffer += token
                token_count += 1
                yield ("expert_token", expert_name, token)
                if token_count >= token_limit:
                    break

        previous_notes += f"{expert_name} says:\n{expert_buffer}\n\n"
        yield ("expert_done", expert_name, expert_buffer)

    # === 4. FINAL VERDICT ===
    yield ("verdict_start", "")

    verdict_prompt = f"""
You are the Final Verdict AI.

Your job:
- Write only 1 paragraph.
- Determine which AI made the best argument and explain why.
- Present 1–2 actionable takeaways.
- Do NOT summarize each expert.
- Do NOT restate the question.

Original prompt:
{user_prompt}

Summary:
{summary_buffer.strip()}

Expert responses:
{previous_notes.strip()}

Final Verdict:
"""

    llm_fn, vcfg = load_model_from_config("jynx_summarizer")
    verdict_buffer = ""

    for chunk in llm_fn(
        verdict_prompt,
        stream_override=True,
        max_tokens=vcfg.get("max_tokens", 1024),
        temperature=vcfg.get("temperature", 0.7),
        stop=get_stop_sequence("jynx_summarizer"),
    ):
        token = chunk.get("choices", [{}])[0].get("text") or \
                chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
        if token:
            verdict_buffer += token
            yield ("verdict_token", token)

    yield ("verdict_done", verdict_buffer)
    yield ("done", "")
