# import asyncio

# LangGraph imports
from langgraph.prebuilt import ToolNode
from langgraph.graph import END

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser

# App specific imports
from tools.escalation import escalate_request
from parser.escalation import TaskParser
from agents.state import AgentState, AgentNames, model_selection
from tools.language import language_prompt
from parser.connectivity import react_parse

class EscalationAgent:
    """Performs network diagnostics like ping, nslookup, whois"""

    def __init__(self, model_name: str = ""):
        self.name = AgentNames.ESCALATION.value
        self.llm = model_selection(model_name)

    def route_condition(self, state: AgentState) -> str:
        """Checks if the tools can be used in the current state"""
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        triage_message = state.get("triage_message", "")
        if triage_message == "FINAL" or state.get("final_answer", ""):
            return END

        if triage_message in [self.name, "ANALYZE"]:
            return self.name

        return self.name

    def __call__(self, state: AgentState) -> AgentState:
        """Executes the connectivity agent logic"""
        user_question = state.get("user_question", "")
        user_language = state.get("user_language", "Spanish")
        triage_message = state.get("triage_message", "")
        user_question = HumanMessage(content=user_question)
        parser = JsonOutputParser(pydantic_object=TaskParser)

        if triage_message == 'ANALYZE':
            system_message = SystemMessage(
                content=f"""Answer the following questions as best you can.
            {language_prompt(user_language)}
            """
            )
            state["escalation_messages"].append(user_question)
            response = self.llm.invoke(state["escalation_messages"])
            state["escalation_messages"].append(response)
            state["final_answer"] = response.content
            state["triage_message"] = "FINAL"

        elif triage_message != self.name:
            system_message = SystemMessage(
                content=f"""
        You are an escalation agent. Your role is to understand the user request and determine if it requires escalation to a higher support level.

        To escalate a request, the user question must pass one of the following conditions:
        1. The question is related to a network issue that requires an external action to solve.
        2. The request involves a **network issue** that cannot be solved without external action.
        3. The user explicitly asks for escalation.

        # Output Rules:
        - If escalation is required, output exactly: ${self.name}
        - If escalation is not required, output exactly: ANALYZE

        # Important:
        - Do not explain your decision.
        - Output must be a single word: either ${self.name} or ANALYZE.
            """
            )
            analyze_message = list()
            analyze_message.append(system_message)
            analyze_message.append(user_question)
            response = self.llm.invoke(analyze_message)
            state["triage_message"] = "ANALYZE"
            if response.content in ["ANALYZE", self.name]:
                state["triage_message"] = response.content

        elif triage_message == self.name:
            system_message = SystemMessage(
                content=f"""
            You are a Product Manager. Your goal is to create product requirements documentation efficiently.
            Follow these rules:
            - Provide a short, concise title that summarizes the task.
            - Provide a detailed description that captures the full context, meaning, and instructions behind the requirement.

            Make sure you fully understand the meaning of each word in the requirements before writing.

            Respond in {user_language}, using the same language as the user requirements to ensure seamless communication.

            Your response MUST follow the format below:
            {{
            "title": "the title of the task",
            "description": "the detailed description of the task"
            }}
            Do not include any explanations or additional text outside the JSON object.
            """
            )
            ticket_list = [system_message]
            ticket_list.append(user_question)
            response = self.llm.invoke(ticket_list)
            values = parser.invoke(response.content)
            from pprint import pprint
            pprint(values)
            ticket_id = escalate_request(
                title=values.get("title", "No title provided."),
                description=values.get("description", "No description provided."),
                question=user_question.content
            )
            system_message = AIMessage(
                content=f"""
            Translate the following ticket information into {user_language}, just give the translation without any additional text:

            New Support Ticket Created:
            - Ticket ID: {ticket_id}
            - Title: {values.get("title", user_question.content)}
            - Description: {values.get("description", "No description provided.")}
            - User Question: {user_question.content}
            """
            )
            state["escalation_messages"].append(system_message)
            response = self.llm.invoke(state["escalation_messages"])
            state["final_answer"] = response.content
            state["triage_message"] = "FINAL"

        return state
