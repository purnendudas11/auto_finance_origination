from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from src.auto_finance_origination.tools.custom_tool import CustomerAgentTool, VehicleAgentTool, RateAgentTool
from crewai import LLM
import os
from bedrock_agentcore.runtime import BedrockAgentCoreApp
app = BedrockAgentCoreApp()
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

llm = LLM(model=os.environ.get('MODEL', 'bedrock/us.amazon.nova-pro-v1:0'), temperature=0)

@CrewBase
class AutoFinanceOrigination():
    """AutoFinanceOrigination crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    # agents_config = 'config/agents.yaml'
    # tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def customer_data_retrieval_specialist(self) -> Agent:
        # from .tools.custom_tool import CustomerAgentTool
        return Agent(
            config=self.agents_config['customer_data_retrieval_specialist'], # type: ignore[index]
            tools=[CustomerAgentTool()],
            llm=llm,
            verbose=True
        )

    @agent
    def vehicle_product_and_inventory_specialist(self) -> Agent:
        # from .tools.custom_tool import VehicleAgentTool
        return Agent(
            config=self.agents_config['vehicle_product_and_inventory_specialist'], # type: ignore[index]
            tools=[VehicleAgentTool()],
            llm=llm,
            verbose=True
        )

    @agent
    def pricing_calculator_specialist(self) -> Agent:
        return Agent(
            config=self.agents_config['pricing_calculator_specialist'], # type: ignore[index]
            tools=[RateAgentTool()],
            llm=llm,
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def customer_data_retrieval_task(self) -> Task:
        return Task(
            config=self.tasks_config['customer_data_retrieval_task'], # type: ignore[index]
        )

    @task
    def vehicle_product_inventory_task(self) -> Task:
        return Task(
            config=self.tasks_config['vehicle_product_inventory_task'], # type: ignore[index]
            output_file='report.md'
        )

    @task
    def pricing_calculator_task(self) -> Task:
        return Task(
            config=self.tasks_config['pricing_calculator_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AutoFinanceOrigination crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

 #3 --------@agentcore.entrypoint decorator- Python decorator within the Bedrock AgentCore SDK--------------------
#  Function to be executed by the runtime on an event (prompt) & Creates WebServer Endpoints
@app.entrypoint
def agent_invocation(payload, context):
    """Handler for agent invocation"""
    print(f'Payload: {payload}')
    try: 
        # Extract user input from payload
        user_input = payload.get("topic", "I want to buy a Toyota car. Can you help me with that?")
        print(f"Processing request: {user_input}")
        
        # Crew Execution - Creates an instance of the AutoFinanceOrigination class and run crew method
        research_crew_instance = AutoFinanceOrigination()
        crew = research_crew_instance.crew()
        # Starts the sequential agent workflow
        result = crew.kickoff(inputs={'topic': user_input})

        print("Context:\n-------\n", context)
        print("Result Raw:\n*******\n", result.raw)
        
        # Safely access json_dict if it exists
        if hasattr(result, 'json_dict'):
            print("Result JSON:\n*******\n", result.json_dict)
        
        return {"result": result.raw}
        
    except Exception as e:
        print(f'Exception occurred: {e}')
        return {"error": f"An error occurred: {str(e)}"}

# Local test function
def test_local():
    """Test the crew locally without AgentCore"""
    try:
        crew_instance = AutoFinanceOrigination()
        crew = crew_instance.crew()
        result = crew.kickoff(inputs={'topic': 'My phone number: 4045551003. I want to buy new Toyota Tacoma. I am not interested in used vehicles. What are the new models available under $70000 and share their details?'})
        print("Result:", result.raw)
        return result
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    app.run(port=8080) 