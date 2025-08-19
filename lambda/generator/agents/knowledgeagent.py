# import asyncio

# LangGraph imports
from langgraph.graph import END

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser

# App specific imports
from tools.vectordb import knowledge_base
from parser.knowledge import KnowledgeRankParser, KnowledgeQAParser
from agents.state import AgentState, AgentNames, model_selection
from tools.language import language_prompt
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser


class KnowledgeAgent:
    """Performs network diagnostics like ping, nslookup, whois"""

    def __init__(self, model_name: str = ""):
        self.name = AgentNames.KNOWLEDGE.value
        self.llm = model_selection(model_name)

    def route_condition(self, state: AgentState) -> str:
        """Checks if the tools can be used in the current state"""
        """
        Use in the conditional_edge to route to the ToolNode if the last message
        has tool calls. Otherwise, route to the end.
        """
        score = state.get("knowledge_score", -1)
        action = state.get("knowledge_action", "")
        final_answer = state.get("final_answer", "")

        if score == -1:
            return self.name
        elif score < 5:
            return AgentNames.ESCALATION.value

        # If there is no action or final answer, we can continue with the knowledge agent
        if not action and not final_answer:
            return self.name

        if action == "escalate":
            return AgentNames.ESCALATION.value
        elif action == "respond" or final_answer:
            return END

        return self.name

    def __call__(self, state: AgentState) -> AgentState:
        """Executes the knowledge agent logic"""
        user_question = state.get("user_question", "")
        user_language = state.get("user_language", "Spanish")
        score = state.get("knowledge_score", -1)
        docs = knowledge_base(question=user_question, num_results=3)
        knowledge_message = []
        if score == -1:
            parser = PydanticOutputParser(pydantic_object=KnowledgeRankParser)
            system_message = SystemMessage(
                content=f"""
            You are a teacher grading a quiz. 

            You will be given a QUESTION and a block of FACTS retrieved from a knowledge source. These FACTS may be unstructured, containing incomplete sentences, lists, bullet points, or unrelated fragments.

            # Your job:

            - Evaluate all the FACTS as a whole to determine whether any part of them contains keywords or semantic meaning related to the QUESTION.
            - If any relevant content exists anywhere in the FACTS, they are considered relevant.

            # Scoring rules (required output):

            Produce a single int score S in the range [0, 10], returned as the only required output (first line).
            - 10 — Direct, accurate, and comprehensive coverage of the QUESTION (facts fully address the question).
            - 8–9 — Highly relevant: most aspects addressed, minor gaps or small omissions.
            - 6–7 — Moderately relevant: useful information present but important parts missing or incomplete.
            - 3–5 — Low relevance: mentions some related keywords or concepts but lacks meaningful substance.
            - 0–2 — Minimal relevance: token or ambiguous mentions that give almost no useful signal.
            - 0 — Completely irrelevant: no overlap with the QUESTION (no keywords, topics, or semantic relation).

            # Reasoning Requirement:

            Explain your reasoning **step-by-step** to show how you evaluated the **entire FACTS block** for relevance.

            # Output Format:

            Your response MUST follow the format below:
            {parser.get_format_instructions()}

            # FACTS:               
            {"\n\n\n -ENTRY: ".join(docs)}
            """
            )
            knowledge_message.append(system_message)
            user_message = HumanMessage(content=f"QUESTION: {user_question}")
            knowledge_message.append(user_message)
            response = self.llm.invoke(knowledge_message)
            score = int(parser.invoke(response).score)
            state["knowledge_score"] = score
        else:
            parser = JsonOutputParser(pydantic_object=KnowledgeQAParser)
            system_message = SystemMessage(
                content=f"""
            You are a knowledge agent. Your role is to answer the user QUESTION using only the information provided in the CONTEXT.
            
            Do not use any external knowledge or make assumptions beyond the CONTEXT.

            # Instructions
            1. Identify: the key scientific concepts, data points, and relevant information in the CONTEXT that pertain directly to the QUESTION.
            2. Analyze: how these elements relate and can be combined to address the QUESTION accurately.
            3. Synthesize: your findings into a clear, concise, and informative answer.

            If the CONTEXT does not contain sufficient information to answer the QUESTION, you must escalate the issue.

            # Important Notes:

            - "action" must be "respond" if the CONTEXT contains enough relevant details to answer the QUESTION, otherwise "escalate".
            - "final_answer" must be fully based on the CONTEXT, with no outside knowledge.
            - Do not output anything other than the JSON object.

            {language_prompt(user_language)}

            Your response MUST follow the format below:
            {parser.get_format_instructions()}

            # CONTEXT:
            {"\n\n\n -ENTRY: ".join(docs)}
            """
            )
            state["messages"].append(system_message)

            # Add user question
            user_message = HumanMessage(content=f"QUESTION: {user_question}")
            state["messages"].append(user_message)

            response = self.llm.invoke(state["messages"])
            values = parser.invoke(response)
            state["final_answer"] = values["final_answer"]
            state["knowledge_action"] = values["action"]
            state["messages"].append(response)
        return state
