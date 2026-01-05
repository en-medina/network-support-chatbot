# import asyncio

# LangGraph imports
from langgraph.prebuilt import ToolNode
from langgraph.graph import END
from langgraph.prebuilt import create_react_agent

# LangChain imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser
from tools.language import language_prompt

# App specific imports
from tools.connection import get_connection_tools, get_connection_tool_names, reset_connected_device
from tools.model import model_selection
from tools.language import language_prompt
from agents.state import AgentState, AgentNames
from parser.device import PlanExecute, RePlan
from parser.connectivity import react_parse

class DeviceAgent:
    """Performs network diagnostics like ping, nslookup, whois"""

    def __init__(self, model_name: str = ""):
        self.name = AgentNames.DEVICE.value
        reset_connected_device()
        self.tools = get_connection_tools()
        self.tool_desc = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in get_connection_tools()]
        )
        self.tool_names = get_connection_tool_names()
        self.llm = model_selection(model_name)
        self.llm_tools = model_selection(model_name, use_huggingface=True)
        self.planner = self._planner_prompt() | self.llm
        self.replanner = self._replan_prompt() | self.llm
        self.summarize = self._summarize_prompt() | self.llm
        self.executor = create_react_agent(
            self.llm_tools, self.tools, prompt=self._executor_prompt()
        )

    def _planner_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([
            SystemMessage(
                content=(
                    "You are an expert problem solver. For the question provided by the user, create a clear, step-by-step plan to solve it. \n"
                    "Requirements for the plan:  \n"
                    "1. Each step should be specific and actionable.  \n"
                    "2. Each step should include enough detail to be executed independently.  \n"
                    "3. No steps should be skipped; include all necessary intermediate steps.  \n"
                    "4. The final step must produce the final answer.  \n"
                    "5. Do not add any irrelevant or superfluous steps.  \n"
                    "Ensure that anyone following your plan, with access to the listed tools, can reach the correct answer without additional guidance.\n"
                    "You must return **only** a JSON object strictly matching this format:\n"
                    "{\n"
                    '  "plan": ["<step 1>", "<step 2>", ...],\n'
                    "}\n\n"
                )
            ),
            ("human", "{input}"),
        ])


    def _summarize_prompt(self) -> ChatPromptTemplate:
        return ChatPromptTemplate.from_messages([("""
You are to summarize the following network diagnostic steps and their results into a concise final answer for the user.
Your summary should include:
1. A brief overview of the original objective.
2. A summary of each diagnostic step taken and its outcome.
3. The final conclusion or answer based on the diagnostics performed.
Follow these rules carefully:
- Keep the summary clear and to the point.
- Do not include unnecessary technical details; focus on what was done and what was found.
- Ensure the final answer directly addresses the user's original question.
- Don't exceed 300 words in total.

**Original Objective**: {user_question}

**Completed Steps**:
{completed_steps}
"""
            )])

    def _replan_prompt(self) -> str:
        return ChatPromptTemplate.from_messages([("""
You are updating an execution plan for solving a given objective.

Your task:
1. Review what the original plan was.
2. Review which steps have already been completed and what was observed or concluded.
3. Decide what still needs to be done — if anything — to reach the final answer.

Follow these rules carefully:
- Include the device name or IP on eac step of the plan if applicable.
- Only include steps that are still needed to complete the objective.
- Do not repeat steps that have already been completed or observed.
- Each remaining step must contain all the information needed to execute it (no skipped logic).
- If all necessary steps are complete and you can produce the final answer, do so.
- **If you reach a point where you cannot make further progress (due to missing information, repeated failures, or no remaining actionable steps), summarize all completed steps and provide the best possible final answer.**
- **In that case, set `"action": "respond"` and include your summary and conclusion in `"response"`.**
- Do not continue replanning indefinitely — you must always either produce new valid steps or provide a final summarized answer.
                                                  
Important: You must eventually reach a final answer. 
If after several completed steps you still cannot resolve the issue, summarize your findings and provide the best answer possible.

Begin!
---

**Objective:**
{input}

**Original Plan:**
{original_plan}

**Completed Steps (with results):**
{past_steps}

Now update your plan.

Return **only** a valid JSON object — with no extra text, comments, or explanations.

Your JSON **must** follow this exact structure:

{{
  "plan": ["<next step 1>", "<next step 2>", "..."],
  "response": "<final answer to the user, or empty string if not ready>",
  "action": "respond" | "replan"
}}
"""
            )])


    def _executor_prompt(self) -> str:
        return (
            "You are a network analysis agent. Your role is to help users diagnose and resolve networking issues "
            "by using the tools provided. You are able to connect to network resources and perform diagnostics "
            "using the available tools. You are knowledgeable in network protocols, diagnostics, configurations, "
            "and common issues related to connectivity, latency, DNS, firewalls, and more. \n\n"
            "Answer the following questions as best you can. You have access to the following tools:\n\n"
            f"{self.tool_desc}\n\n"
            "Only use tools when absolutely necessary. If you have all the information you need to answer the question "
            "based on previous messages, you may skip the tools and go straight to the final answer. \n\n"
            "Use the following format:\n\n"
            "Question: the input question you must answer\n"
            "Thought: you should always think about what to do\n"
            f"Action: the action to take, should be one of [{self.tool_names}]\n"
            "Action Input: the input to the action\n"
            "Observation: the result of the action\n"
            "... (this Thought/Action/Action Input/Observation can repeat N times)\n"
            "Thought: I now know the final answer\n"
            "Final Answer: the final answer to the original input question\n\n"
            "Important: You must eventually reach a final answer. Do not continue using tools indefinitely. "
            "If after several steps you still cannot resolve the issue, summarize your findings and provide the best answer possible. \n\n"
            "Begin!"
        )
    
    def planner_step(self, state: AgentState) -> AgentState:
        res = self.planner.invoke({"input": state["user_question"]})
        parser = JsonOutputParser(pydantic_object=PlanExecute)
        ans = parser.invoke(res)
        state["device_plan"] = ans["plan"]
        return state
    
    def executor_step(self, state: AgentState) -> AgentState:
        plan_str = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(state["device_plan"]))
        first_step = state["device_plan"][0] if state["device_plan"] else ""
        user_prompt = f"For the following plan:\n{plan_str}\n\nYou are tasked with executing step 1, {first_step}."
        res = self.executor.invoke(
            {"messages": [
                HumanMessage(content=user_prompt)]},
            config={"recursion_limit": 10}
        )
        ans = react_parse(res["messages"][-1])
        state["device_past_steps"].append((first_step, ans["final_answer"]))
        return state
    
    def replan_step(self, state: AgentState) -> AgentState:
        plan_str = "\n".join(f"{i + 1}. {step}" for i, step in enumerate(state["device_plan"]))
        previous_plan =  "\n".join("previous step: " + step + " result: " + res for step, res in state["device_past_steps"])
        res = self.replanner.invoke({
            "input": state["user_question"],
            "original_plan": plan_str,
            "past_steps": previous_plan
        })
        parser = JsonOutputParser(pydantic_object=RePlan)
        ans = parser.invoke(res)
        state["device_plan"] = ans["plan"]
        state["final_answer"] = ans["response"]
        state["device_action"] = ans["action"]
#        state["final_answer"] = res.content
        return state

    def summarize_step(self, state: AgentState) -> AgentState:
        completed_steps = "\n".join("previous step: " + step + " result: " + res for step, res in state["device_past_steps"])
        res = self.summarize.invoke({
            "user_question": state["user_question"], 
            "completed_steps": completed_steps
        })
        state["final_answer"] = res.content
        state["device_action"] = "respond"
        return state

    def route_condition(self, state: AgentState) -> str:
        """Determine if this agent should be invoked based on the state"""
        
        # if it has not yet started need to run planner
        if state.get("device_iteration", 0) == 0:
            return AgentNames.DEVICE.value
        
        # if action is replan need to re-invoke
        if state.get("device_action", "") == "replan":
            return AgentNames.DEVICE.value
        
        # if action is respond and final answer is set, we can end
        if state.get("device_action", "respond") == "respond" and state.get("final_answer", ""):
            return END

        # otherwise continue with device agent
        return AgentNames.DEVICE.value        

    def __call__(self, state) -> AgentState:
        # First iteration: plan
        if state["device_iteration"] == 0:
            state = self.planner_step(state)

        if state["device_iteration"] < 5:
            # Subsequent iterations: execute and replan
            state = self.executor_step(state)
            state = self.replan_step(state)
        else:
            # Final iteration: summarize
            state = self.summarize_step(state)
        state["device_iteration"] += 1
        return state
