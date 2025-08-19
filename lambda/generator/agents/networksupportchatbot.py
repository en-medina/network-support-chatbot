# import asyncio
import re

# LangGraph imports
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# LangChain imports
from langchain.callbacks.tracers import ConsoleCallbackHandler

# App specific imports
from agents.state import AgentState
from agents import ConnectivityAgent, TriageAgent, KnowledgeAgent, EscalationAgent
from tools.language import detect_language
import settings

class NetworkSupportChatbot:
    """Main chatbot class that orchestrates the multi-agent system"""

    def __init__(self):
        # Initialize agents
        ENVIRONMENT = settings.ENVIRONMENT

        triage_model_name = "hf.co/sungun19961/Network-Route-Agent:Q4_K_M"
        if ENVIRONMENT == "production":
            triage_model_name = "arn:aws:bedrock:us-east-1:783111403365:imported-model/k2dmo31xmct9"

        self.triage_agent = TriageAgent(model_name=triage_model_name)
        self.connectivity_agent = ConnectivityAgent()
        self.knowledge_agent = KnowledgeAgent()
        self.escalation_agent = EscalationAgent()

        # Create workflow
        self.workflow = self._create_workflow()

        # Create app with checkpointer
        memory = MemorySaver()
        self.app = self.workflow.compile(checkpointer=memory)

    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow"""
        workflow = StateGraph(AgentState)

        # Add nodes
        workflow.add_node(self.connectivity_agent.name, self.connectivity_agent)
        workflow.add_node(self.connectivity_agent.tool_node.name, self.connectivity_agent.tool_node)
        workflow.add_node(self.triage_agent.name, self.triage_agent)
        workflow.add_node(self.knowledge_agent.name, self.knowledge_agent)
        workflow.add_node(self.escalation_agent.name, self.escalation_agent)
        workflow.add_node(self.escalation_agent.tool_node.name, self.escalation_agent.tool_node)
        
        # Add Triage Edges
        workflow.add_edge(START, self.triage_agent.name)
        workflow.add_conditional_edges(
            self.triage_agent.name,
            self.triage_agent.route_condition,
        )

        # Add Connectivity Edges
        workflow.add_conditional_edges(
            self.connectivity_agent.name,
            self.connectivity_agent.route_condition,
        )
        workflow.add_edge(
            self.connectivity_agent.tool_node.name, self.connectivity_agent.name
        )

        # Add Knowledge Edges
        workflow.add_conditional_edges(
            self.knowledge_agent.name,
            self.knowledge_agent.route_condition,
        )

        # Add Connectivity Edges
        workflow.add_conditional_edges(
            self.escalation_agent.name,
            self.escalation_agent.route_condition,
        )
        workflow.add_edge(
            self.escalation_agent.tool_node.name, self.escalation_agent.name
        )

        # Add Initial and Final Edges
        # workflow.add_edge(END, self.connectivity_agent.name)
        return workflow

    def process_question(self, question: str, thread_id: str = "default", debug: bool = False) -> str:
        """Process a user question through the multi-agent system"""

        # Initialize state
        initial_state = AgentState(
            messages=[],
            tool_messages=[],
            user_question=question,
            knowledge_score=-1,
            knowledge_action="",
            final_answer="",
            user_language=detect_language(question),
            triage_message="",
        )

        # Configure thread
        config = {
            "configurable": {
                "thread_id": thread_id
            },
            "callbacks": [ConsoleCallbackHandler()]
        }

        # Run workflow
        result = self.app.invoke(initial_state, config=config)

        messages = result.get("messages", [])
        final_answer = result.get("final_answer", "")
        if final_answer:
            return final_answer
        if messages:
            return self._parse(messages[-1].content)
        return "Lo siento, no pude procesar tu solicitud."

    def _parse(self, text: str) -> str:
        """Parse the final answer from the text"""
        if "Final Answer:" in text:
            match = re.search(r"Final Answer:\s*(.+)", text, re.DOTALL)
            if match:
                return match.group(1).strip()
        return text
