# import asyncio

# LangGraph imports
from langgraph.prebuilt import ToolNode
from langgraph.graph import END

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# App specific imports
from tools.network import get_network_tools, get_network_tool_names
from tools.model import model_selection
from tools.language import language_prompt
from agents.state import AgentState, AgentNames
from parser.connectivity import react_parse

class ConnectivityAgent:
    """Performs network diagnostics like ping, nslookup, whois"""

    def __init__(self, model_name: str = ""):
        self.name = AgentNames.CONNECTIVITY.value
        self.llm = model_selection(model_name, use_huggingface=True)
        self.tools = get_network_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_node = ToolNode(tools=self.tools, name="connectivity_tools", messages_key="tool_messages")

    def route_condition(self, state: AgentState) -> str:
        """Checks if the tools can be used in the current state"""
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        messages = state.get("messages", [])
        # If there are no messages, we cannot route
        if not messages:
            raise ValueError("No messages found in state to route_condition")

        last_message = messages[-1]

        if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
            return self.tool_node.name
        # If the final answer is already set, we can end the conversation
        if state.get("final_answer", ""):
            return END

        return self.name

    def __call__(self, state: AgentState) -> AgentState:
        """Executes the connectivity agent logic"""
        user_question = state.get("user_question", "")
        user_language = state.get("user_language", "Spanish")

        tool_names = get_network_tool_names()
        tools_desc = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools]
        )

        if not state.get("messages", []):
            system_message = SystemMessage(
                content=f"""
            You are a network connectivity agent. Your role is to help users diagnose and resolve networking issues by using the tools provided. 
            You are knowledgeable in network protocols, diagnostics, configurations, and common issues related to connectivity, latency, DNS, firewalls, and more.

            Answer the following questions as best you can. You have access to the following tools:

            {tools_desc}

            Only use tools when absolutely necessary. If you have all the information you need to answer the question based on previous messages, 
            you may skip the tools and go straight to the final answer.

            Use MUST use the following format:

            Question: the input question you must answer
            Thought: you should always think about what to do, do not use any tool if it is not needed. 
            Action: the action to take, should be one of [{tool_names}]
            Action Input: the input to the action
            Observation: the result of the action
            If the observation does not help you make further progress, consider stopping and providing the final answer with your current best reasoning.
            ... (this Thought/Action/Action Input/Observation can repeat N times)
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question.

            If no tools are needed, use this simpler format:

            Question: the input question you must answer  
            Thought: I already know the answer based on the information provided  
            Final Answer: the final answer to the original input question.

            Important: You must eventually reach a final answer. Do not continue using tools indefinitely. 
            If after several steps you still cannot resolve the issue, summarize your findings and provide the best answer possible.

            To stop iteration you MUST write Final Answer: and provide the answer.

            Begin!
            """
            )
            state["messages"].append(system_message)
            # Add user question
            user_message = HumanMessage(content=f"Question: {user_question}")
            state["messages"].append(user_message)

        if state.get("tool_messages", []):
            print(state['messages'][-1])
            tool_message = AIMessage(
                content=f"""**** Tool Response *******
                Action: {state['messages'][-1].tool_calls[0]['name']}
                Action Input: {state['messages'][-1].tool_calls[0]['args']}
                Observation: {state['tool_messages'][-1].content}"""
            )
            state["messages"].append(tool_message)
            state["tool_messages"] = []

        response = self.llm_with_tools.invoke(state["messages"])
        parsed_response = react_parse(response)

        # Process response
        state["messages"].append(response)
        state["final_answer"] = parsed_response.get("final_answer", "")
        if state["final_answer"]:
            state["final_answer"] = self.llm.invoke([
                SystemMessage(
                    content=f"""Translate the following text into {user_language}, just give the translation without any additional text:
                    {state["final_answer"]}
                    """
                )
            ]).content
        if hasattr(response, "tool_calls") and len(response.tool_calls) > 0:
            state["tool_messages"].append(response)
        return state
