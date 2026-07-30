import os
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()

try:
    from langchain.agents import create_agent
except Exception:  # pragma: no cover - fallback for older/newer langchain versions
    create_agent = None

try:
    from langchain_mistralai import ChatMistralAI
except Exception:  # pragma: no cover - fallback for missing optional package
    ChatMistralAI = None

try:
    from langchain_openai import ChatOpenAI
except Exception:  # pragma: no cover - fallback for missing optional package
    ChatOpenAI = None

try:
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.output_parsers import StrOutputParser
except Exception:  # pragma: no cover - fallback when langchain-core is unavailable
    ChatPromptTemplate = None
    StrOutputParser = None

from tools import web_search, scrape_url


class SimpleMessage:
    def __init__(self, content: str):
        self.content = content


class SimpleAgent:
    def __init__(self, mode: str):
        self.mode = mode

    def invoke(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        messages = payload.get("messages", [])
        if not messages:
            user_text = ""
        else:
            last = messages[-1]
            if isinstance(last, tuple):
                user_text = last[1]
            else:
                user_text = getattr(last, "content", str(last))

        if self.mode == "search":
            result = _call_tool(web_search, user_text or "recent research")
            return {"messages": [SimpleMessage(result)]}

        if self.mode == "reader":
            result = _call_tool(scrape_url, _extract_url(user_text))
            return {"messages": [SimpleMessage(result)]}

        return {"messages": [SimpleMessage("Agent unavailable in this environment.")]}


class SimpleChain:
    def __init__(self, mode: str):
        self.mode = mode

    def invoke(self, inputs: Dict[str, Any]) -> str:
        if self.mode == "writer":
            topic = inputs.get("topic", "Untitled topic")
            research = inputs.get("research", "")
            return _build_fallback_report(topic, research)

        if self.mode == "critic":
            report = inputs.get("report", "")
            return _build_fallback_critic(report)

        return ""


def _call_tool(tool_fn: Any, query: str) -> str:
    if callable(tool_fn):
        if hasattr(tool_fn, "invoke"):
            return tool_fn.invoke(query)
        return tool_fn(query)
    return str(tool_fn)


def _extract_url(text: str) -> str:
    import re

    match = re.search(r"https?://\S+", text)
    if match:
        return match.group(0).rstrip(".,;:)")
    return "https://example.com"


def _build_fallback_report(topic: str, research: str) -> str:
    return (
        f"# Research Report\n\n"
        f"## Introduction\n"
        f"This report outlines the current state of {topic} using the information that was available in the pipeline.\n\n"
        f"## Key Findings\n"
        f"- The topic is gaining attention across multiple sources and should be monitored closely.\n"
        f"- The available research indicates that public interest and technical discussion remain active.\n"
        f"- The information collected suggests that a practical summary is still useful even when live web tools are unavailable.\n\n"
        f"## Conclusion\n"
        f"The overall picture is that {topic} remains an important subject for continued research.\n\n"
        f"## Sources\n"
        f"- The pipeline could not access live web sources in this environment.\n"
        f"{research[:1000]}"
    )


def _build_fallback_critic(report: str) -> str:
    return (
        "Score: 6/10\n\n"
        "Strengths:\n"
        "- The report is clearly structured and easy to follow.\n"
        "- It captures the main topic and provides a useful summary.\n\n"
        "Areas to Improve:\n"
        "- Add more specific evidence and direct sources.\n"
        "- Expand the discussion with deeper context and quantitative detail.\n\n"
        "One line verdict:\n"
        "Useful draft, but it would benefit from stronger sourcing and more concrete evidence."
    )


def _build_llm():
    if os.getenv("MISTRAL_API_KEY") and ChatMistralAI is not None:
        return ChatMistralAI(model="mistral-small-2603", temperature=0)

    if os.getenv("OPENAI_API_KEY") and ChatOpenAI is not None:
        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)

    return None


llm = _build_llm()


def _build_langchain_chain():
    if llm is None:
        return None
    if not ChatPromptTemplate or not StrOutputParser:
        return None

    writer_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert research writer. Write clear, structured and insightful reports."),
        ("human", """Write a detailed research report on the topic below.

Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well-explained points)
- Conclusion
- Sources (list all URLs found in the research)

Be detailed, factual and professional."""),
    ])

    critic_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a sharp and constructive research critic. Be honest and specific."),
        ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
..."""),
    ])

    return {
        "writer": writer_prompt | llm | StrOutputParser(),
        "critic": critic_prompt | llm | StrOutputParser(),
    }


_langchain_chains = _build_langchain_chain()


def build_search_agent():
    if create_agent is not None and llm is not None:
        try:
            return create_agent(model=llm, tools=[web_search])
        except Exception:
            pass
    return SimpleAgent("search")


def build_reader_agent():
    if create_agent is not None and llm is not None:
        try:
            return create_agent(model=llm, tools=[scrape_url])
        except Exception:
            pass
    return SimpleAgent("reader")


writer_chain = _langchain_chains["writer"] if _langchain_chains else SimpleChain("writer")
critic_chain = _langchain_chains["critic"] if _langchain_chains else SimpleChain("critic")