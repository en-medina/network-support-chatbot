import re

# LangChain imports
from langchain_core.messages import HumanMessage, SystemMessage

# App specific imports
from agents.state import AgentState, AgentNames, model_selection


class TriageAgent:
    """Decides which agent to route the user question to based on the content of the question"""

    def __init__(self, model_name: str = ""):
        self.name = AgentNames.TRIAGE.value
        self.llm = model_selection(model_name)

    def route_condition(self, state: AgentState) -> str:
        """
        Determines which agent to route to based on the LLM's response.
        Expects the last message to contain 'Final Answer: agent_name'.
        Defaults to 'knowledge' if unclear.
        """
        default_agent = AgentNames.KNOWLEDGE.value
        valid_agents = AgentNames.list()
        agent_name = None

        triage_message = state.get("triage_message", "")

        # Extract agent name from the last message
        match = re.search(r"Final Answer:\s*(\w+)", triage_message, re.IGNORECASE)
        if match:
            agent_name = match.group(1).upper()

        # if is self agent, return default agent
        if agent_name == self.name:
            return default_agent
        # Return the agent name if valid, otherwise return the default agent
        if agent_name in valid_agents:
            return agent_name
        return default_agent

    def __call__(self, state: AgentState) -> AgentState:
        """Executes the connectivity agent logic"""
        user_question = state.get("user_question", "")
        messages = list()
        system_message = SystemMessage(
            content=f"""
    You are a routing triage agent. Your job is to choose the right agent to handle each user request. The available agents are:

    - knowledge: Retrieves and summarizes information from documentation and various sources. Use this agent when the request is informational or unclear.
    - escalation: Handles unresolved, complex, or critical issues that require human intervention or higher-level support.
    - connectivity: Performs network diagnostics such as ping tests, port checks, and DNS queries.
    - device: Interacts directly with network devices to perform read and limited write operations.

    When a user request is received, evaluate the content and determine the most appropriate agent to handle it.
    If the appropriate destination is unclear, default to the knowledge agent.

    Respond using the following format:

    ```
    Final Answer: the name of the selected agent
    ```

    Do not explain your choice, just give the agent name.
        """
        )
        messages.append(system_message)
        user_message = HumanMessage(content=f"Question: {user_question}")
        messages.append(user_message)

        # Call the LLM with tools
        response = self.llm.invoke(messages)
        # Process response

        if hasattr(response, "content"):
            state["triage_message"] = response.content
            
        return state
