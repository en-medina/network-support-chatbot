import asyncio
import json

# LangGraph imports
from langgraph.graph import END

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.language_models import BaseChatModel
from langchain_core.output_parsers import PydanticOutputParser

# App specific imports
from tools.vectordb import knowledge_base
from parser.knowledge import KnowledgeRankParser, KnowledgeQAParser
from agents.state import AgentState, AgentNames
from tools.language import language_prompt
import re
from langchain_core.output_parsers import PydanticOutputParser


class KnowledgeAgent:
    """Performs network diagnostics like ping, nslookup, whois"""

    def __init__(self, llm: BaseChatModel = None):
        self.name = AgentNames.KNOWLEDGE.value
        if llm is None:
            self.llm = ChatOllama(model="llama3.2:3b", temperature=0)
        else:
            self.llm = llm

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
        elif score < 0.5:
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

                You will be given a QUESTION and a set of FACTS provided by the student. 

                Here is the grade criteria to follow:
                (1) You goal is to identify FACTS that are completely unrelated to the QUESTION
                (2) If the facts contain ANY keywords or semantic meaning related to the question, consider them relevant
                (3) It is OK if the facts have SOME information that is unrelated to the question (2) is met 

                Score:
                A score of 1 means that the FACT contain ANY keywords or semantic meaning related to the QUESTION and are therefore relevant. This is the highest (best) score. 
                A score of 0 means that the FACTS are completely unrelated to the QUESTION. This is the lowest possible score you can give.

                Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct.

                your response must be in the following format:

                Question: the input question you must answer
                Thought: Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 
                Score: Only return a score from 0 to 1. Do not provide any additional explanation or context.

                FACTS: {"\n\n\n -ENTRY: ".join(docs)}
            """
            )
            knowledge_message.append(system_message)
            user_message = HumanMessage(content=f"QUESTION: {user_question}")
            knowledge_message.append(user_message)
            response = self.llm.invoke(knowledge_message)
            score = parser.invoke(response).score
            state["knowledge_score"] = score
        else:
            parser = PydanticOutputParser(pydantic_object=KnowledgeQAParser)
            system_message = SystemMessage(
                content=f"""
            You are a knowledge agent. Your role is to answer the user QUESTION using only the information provided in the CONTEXT. Do not use any external knowledge or make assumptions beyond the CONTEXT.

            # Instructions
            1. Identify: the key scientific concepts, data points, and relevant information in the CONTEXT that pertain directly to the QUESTION.
            2. Analyze: how these elements relate and can be combined to address the QUESTION accurately.
            3. Synthesize: your findings into a clear, concise, and informative answer.

            If the CONTEXT does not contain sufficient information to answer the QUESTION, you must escalate the issue.

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
            state["final_answer"] = values.final_answer
            state["knowledge_action"] = values.action
            state["messages"].append(response)
        return state
