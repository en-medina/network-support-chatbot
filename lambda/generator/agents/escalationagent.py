# import asyncio

# LangGraph imports
from langgraph.prebuilt import ToolNode
from langgraph.graph import END

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# App specific imports
from tools.escalation import get_escalation_tools, get_escalation_tool_names
from agents.state import AgentState, AgentNames, model_selection
from tools.language import language_prompt
from parser.connectivity import react_parse

class EscalationAgent:
    """Performs network diagnostics like ping, nslookup, whois"""

    def __init__(self, model_name: str = ""):
        self.name = AgentNames.ESCALATION.value
        self.llm = model_selection(model_name, use_huggingface=True)
        self.tools = get_escalation_tools()
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        self.tool_node = ToolNode(tools=self.tools, name="escalation_tools", messages_key="tool_messages")

    def route_condition(self, state: AgentState) -> str:
        """Checks if the tools can be used in the current state"""
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        messages = state.get("escalation_messages", [])
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

        tool_names = get_escalation_tool_names()
        tools_desc = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools]
        )

        if not state.get("tool_messages", []):
            system_message = SystemMessage(
                content=f"""
    You are an escalation agent. Your role is to understand the user request and determine if it requires escalation to a higher support level.

    To escalate a request, the user question must pass one of the following conditions:
    1. The question is related to a network issue that requires an external action to solve.  
    2. The user explicitly requests that you escalate the question.  
    3. The question was received from the knowledge, device, or connectivity agent and the question hasn't been addressed.  
    
    You should always think about what to do, and do NOT create a ticket if it is not needed.
    If you create a ticket, you MUST include the ticket ID in your final answer.
    You can go directly to the final response if no escalation is needed.

    If the above conditions are not met, answer the user request as best you can.

    If after reasoning and trying possible steps you still cannot resolve the issue, stop and provide a summary of your findings as the final answer. Do not keep using tools indefinitely. 

    You have access to the following tools:

    {tools_desc}

    Only use the tool when absolutely necessary. If you have all the information you need to answer the question based on previous messages, skip the tool and go straight to the final answer.

    You MUST use the following format when tools are needed:

    Question: the input question you must answer
    Thought: you should always think about what to do, do not use any tool if it is not needed. 
    Action: the action to take, should be one of [{tool_names}]
    Action Input: the input to the action
    Observation: the result of the action
    If the observation does not help you make further progress, consider stopping and providing the final answer with your current best reasoning.
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I now know the final answer
    Final Answer: the final answer to the original input question. If you had created a ticket, provide the ticket ID on your answer.

    If no tools are needed, use this simpler format: 

    Question: the input question you must answer  
    Thought: I already know the answer based on the information provided  
    Final Answer: the final answer to the original input question. If you had created a ticket, provide the ticket ID on your answer.

    IMPORTANT: You must eventually reach a final answer.  
    If no clear solution exists, stop and provide the best possible summary.

    {language_prompt(user_language)}

    Begin!
            """
            )
            state["escalation_messages"].append(system_message)

            # Add user question
            user_message = HumanMessage(content=f"Question: {user_question}")
            state["escalation_messages"].append(user_message)
        else:
            state["escalation_messages"].extend(state["tool_messages"])
            state["tool_messages"] = []

        response = self.llm_with_tools.invoke(state["escalation_messages"])
        parsed_response = react_parse(response)

        # Process response
        state["escalation_messages"].append(response)
        state["final_answer"] = parsed_response.get("final_answer", "")
        state["tool_messages"].append(response)
        return state
