from langgraph.prebuilt import create_react_agent
from tools.model import model_selection
from tools.connection import get_connection_tools, get_connection_tool_names
from tools.network import get_network_tools, get_network_tool_names

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage


def test_executor():
    llm = model_selection("llama3.2:3b", use_huggingface=True)
    tools = get_network_tools()
    tools_desc = "\n".join(
        [f"{tool.name}: {tool.description}" for tool in tools]
    )
    tools_names = get_network_tool_names()
    system_message = """
    You are a network connectivity agent. Your role is to help users diagnose and resolve networking issues by using the tools provided. You are knowledgeable in network protocols, diagnostics, configurations, and common issues related to connectivity, latency, DNS, firewalls, and more.

    Answer the following questions as best you can. You have access to the following tools:

    {tools_desc}

    Only use tools when absolutely necessary. If you have all the information you need to answer the question based on previous messages,
    you may skip the tools and go straight to the final answer.

    Use the following format:

    Question: the input question you must answer
    Thought: you should always think about what to do, do not use any tool if it is not needed. 
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    If the observation does not help you make further progress, consider stopping and providing the final answer with your current best reasoning.
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question.

    Important: You must eventually reach a final answer. Do not continue using tools indefinitely. 
    If after several steps you still cannot resolve the issue, summarize your findings and provide the best answer possible.

    Begin!
    """

    agent_executor = create_react_agent(llm, get_network_tools(), prompt=system_message)
    human_msg = [HumanMessage(content=f"Question: What are the IP addresses of the domain www.bohiio.com?")]

    # Stream intermediate steps
    res = agent_executor.invoke(
        {"messages": human_msg}, stream_intermediate_steps=True,
        config={"recursionLimit": 10}
    )
    print(res["messages"][-1].content)

def test_planner():
    from pprint import pprint
    from agents.deviceagent import DeviceAgent
    import settings

    agent = DeviceAgent(model_name=settings.LLAMA32_MODEL_ARN)
    x = agent("Is the interface Eth 0/0 enable on main-router?")
    pprint(x)

if __name__ == "__main__":
    test_planner()
