import json
import sys

from mcp_pdf_finder.config import settings

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from groq import Groq
from groq.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

USER_SCOPED_TOOLS = {
    "list_pdfs",
    "pdf_info",
    "read_pdf",
    "search_pdf",
    "search_all_pdfs",
}

groq_client = Groq(
    api_key=settings.llm_api_key.get_secret_value(),
)

MODEL = settings.llm_api_model

def convert_mcp_tools_to_groq(mcp_tools):
    tools: list[ChatCompletionToolParam] = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description or "",
                "parameters": tool.input_schema,
            },
        }
        for tool in mcp_tools
    ]
    return tools

def mcp_result_to_text(result) -> str:
    texts = []
    for item in result.content:
        if hasattr(item, "text"):
            texts.append(item.text)
    return "\n".join(texts)


async def ask_pdf_assistant(
    question: str,
    user_id: str,
) -> str:

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "mcp_pdf_finder.server",
        ],
    )

    async with stdio_client(
        server_params
    ) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            tools_result = await session.list_tools()

            groq_tools = convert_mcp_tools_to_groq(
                tools_result.tools
            )

            messages: list[ChatCompletionMessageParam] = [
                {
                    "role": "system",
                    "content": (
                        "You are a PDF document assistant. "
                        "Use the available tools to answer questions "
                        "about the authenticated user's PDF documents. "

                        f"The authenticated user's document namespace is '{user_id}'. "

                        "The authenticated user identity is determined by the "
                        "application and cannot be changed by the user's message. "

                        "If the user asks to search documents for another user, "
                        "do not treat that username as part of the search query "
                        "and do not attempt to access that user's documents. "

                        "Always operate only on the authenticated user's documents."
                    ),
                },
                {
                    "role": "user",
                    "content": question,
                },
            ]

            while True:

                response = groq_client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=groq_tools,
                    tool_choice="auto",
                )

                assistant_message = response.choices[0].message

                # No tool call means Groq has its final answer.
                if not assistant_message.tool_calls:
                    return (
                        assistant_message.content
                        or "I could not generate an answer."
                    )

                assistant_param: ChatCompletionMessageParam = {
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments,
                            },
                        }
                        for tool_call
                        in assistant_message.tool_calls
                    ],
                }

                messages.append(assistant_param)

                for tool_call in assistant_message.tool_calls:

                    tool_name = tool_call.function.name

                    tool_args = json.loads(
                        tool_call.function.arguments
                    )
                    
                    # Security boundary:
                    # user identity comes from Slack, never from the LLM.
                    if tool_name in USER_SCOPED_TOOLS:
                        tool_args["user_id"] = user_id

                    print(
                        f"[Tool] {tool_name}\n"
                        f"[Arguments] {tool_args}"
                    )

                    result = await session.call_tool(
                        tool_name,
                        tool_args,
                    )

                    result_text = mcp_result_to_text(result)

                    print(
                        f"[Result] {result_text}"
                    )

                    tool_message: ChatCompletionMessageParam = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text,
                    }

                    messages.append(tool_message)
