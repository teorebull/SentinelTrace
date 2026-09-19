from ollama import ChatResponse, chat


def ask_model(
    messages: list[dict], tools: list[dict], model: str = "qwen3"
) -> ChatResponse:
    """
    Send messages to Ollama and return the model response.
    """
    response = chat(messages=messages, tools=tools, model=model)
    return response
