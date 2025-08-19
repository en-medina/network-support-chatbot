from langchain_core.messages import BaseMessage
import re

def react_parse(message: BaseMessage) -> dict:
    """Parse a message to extract the final answer"""
    ans = {
        "final_answer": "",
        "question": "",
        }
    message_content = message.content if hasattr(message, "content") else ""
    # Question Extraction
    match = re.search(r"Question:\s*(.+)", message_content, re.DOTALL | re.IGNORECASE)
    if match:
        ans["question"] = match.group(1).strip()
    # Final Answer Extraction
    match = re.search(r"Final Answer:\s*(.+)", message_content, re.DOTALL | re.IGNORECASE)
    if match:
        ans["final_answer"] = match.group(1).strip()
    return ans