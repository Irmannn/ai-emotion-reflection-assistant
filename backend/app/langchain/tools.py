from typing import Annotated, Any

from langchain_core.tools import BaseTool, tool


@tool
def list_reflections(limit: Annotated[int, "Maximum number of records to return, between 1 and 10."] = 5) -> str:
    """List recent emotion reflection records for the current user session."""
    raise RuntimeError("Tool schemas are executed by app.agent.tool_runner, not directly by LangChain.")


@tool
def search_reflections(
    query: Annotated[str, "One or more concise keywords separated by spaces."],
    limit: Annotated[int, "Maximum number of records to return, between 1 and 10."] = 5,
) -> str:
    """Search current-session reflections by keywords, emotion tags, focus areas, or report content."""
    raise RuntimeError("Tool schemas are executed by app.agent.tool_runner, not directly by LangChain.")


@tool
def get_reflection_detail(record_id: Annotated[int, "Reflection record ID returned by a previous search."]) -> str:
    """Get full detail for one reflection record in the current user session."""
    raise RuntimeError("Tool schemas are executed by app.agent.tool_runner, not directly by LangChain.")


@tool
def search_knowledge_base(
    query: Annotated[str, "Question or concise keywords to search in the shared built-in knowledge base."],
    limit: Annotated[int, "Maximum number of knowledge references to return, between 1 and 5."] = 3,
) -> str:
    """Search built-in emotion reflection materials for theory, exercises, or practical suggestions."""
    raise RuntimeError("Tool schemas are executed by app.agent.tool_runner, not directly by LangChain.")


def get_agent_tools() -> list[BaseTool]:
    return [list_reflections, search_reflections, get_reflection_detail, search_knowledge_base]
