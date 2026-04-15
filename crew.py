# crew.py
import os
import yaml
from dotenv import load_dotenv
from typing import List

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from chromadb import PersistentClient

from tools.Goal_Calculation import CalculateGoalsTool
from pathlib import Path

# Store in project directory
# project_root = Path(__file__).parent
# storage_dir = project_root / "crewai_storage"

# os.environ["CREWAI_STORAGE_DIR"] = str(storage_dir)

os.environ["CREWAI_STORAGE_DIR"] = "./my_project_storage"

# ✅ Embedder for memory
embedder_config = {
    "provider": "openai",
    "config": {
        "model": 'text-embedding-3-small'
    }
}
load_dotenv()

# ✅ Persistent memory store
chroma_client = PersistentClient(path="./chroma_memory")

@CrewBase
class ICAgents:
    """CrewAI Chatbot Crew - ICAgents"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self):
        with open("config/agents.yaml", "r", encoding="utf-8") as f:
            self.agents_config = yaml.safe_load(f)
        with open("config/tasks.yaml", "r", encoding="utf-8") as f:
            self.tasks_config = yaml.safe_load(f)

    @agent
    def user_interaction_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['user_interaction_agent'],
            llm=os.getenv("MODEL"),
            memory=True,
            memory_id="user_interaction_agent",
            verbose=True
        )

    @agent
    def goal_calculation_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['goal_calculation_agent'],
            llm=os.getenv("MODEL"),
            memory=True,
            memory_id="goal_calculation_agent",
            tools=[CalculateGoalsTool()],
            allow_delegation=False,
            verbose=True
        )

    def intent_task(self) -> Task:
        return Task(
            config=self.tasks_config['interpret_user_request'],
            memory=True
        )

    @task
    def compute_ic_goals(self) -> Task:
        return Task(
            config=self.tasks_config['compute_ic_goals']
        )

    def input_crew(self) -> Crew:
        return Crew(
            agents=[self.user_interaction_agent()],
            tasks=[self.intent_task()],
            process=Process.sequential,
            memory=True,
            memory_store=chroma_client,
            embedder=embedder_config,
            verbose=True
        )

    @crew
    def calculate(self) -> Crew:
        return Crew(
            agents=[self.goal_calculation_agent()],
            tasks=[self.compute_ic_goals()],
            process=Process.sequential,
            memory=True,
            memory_store=chroma_client,
            embedder=embedder_config,
            verbose=True
        )

    # def has_required_info(self) -> bool:
    #     """Check memory for both quarter and national goal"""
    #     memory = self.user_interaction_agent().memory
    #     entities = memory.recall_all()

    #     has_quarter = any("quarter" in e.lower() for e in entities)
    #     has_goal = any("goal" in e.lower() and any(char.isdigit() for char in e) for e in entities)
    #     return has_quarter and has_goal

if __name__ == "__main__":
    crew_instance = ICAgents()
    crew = crew_instance.input_crew()  # Only do this once!


    while True:
        print("\n--- Awaiting Input ---")
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit", "q"]:
            print("Exiting...")
            break

        print(f"🔍 Processing user input: '{user_input}'")

        input_result = crew.kickoff(inputs={"user_input": user_input})
        print("🤖 Input Crew Result:", input_result)

        # if crew_instance.has_required_info():
        #     print("✅ All info present. Proceeding to calculation...")
        #     calc_result = crew_instance.calculate().kickoff()
        #     print("🎯 Calculation Result:", calc_result)
        # else:
        #     print("📝 Awaiting more input: please provide missing quarter or national goal if not yet given.")
