from crewai import Agent, Crew, Process, Task
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel


# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# Define the Pydantic model for the blog
class Review(BaseModel):
    issues: str

@CrewBase
class CodeReview():
	"""CodeReview crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def developer(self) -> Agent:
		return Agent(
			config=self.agents_config['developer'],
			verbose=True
		)

	@agent
	def tester(self) -> Agent:
		return Agent(
			config=self.agents_config['tester'],
			verbose=True,
		)

	@agent
	def report_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['report_analyst'],
			verbose=True
		)

	@task
	def developer_task(self) -> Task:
		return Task(
			config=self.tasks_config['developer_task'],
		)

	@task
	def tester_task(self) -> Task:
		return Task(
			config=self.tasks_config['tester_task'],
		)

	@task
	def report_analyst_task(self) -> Task:
		return Task(
			config=self.tasks_config['report_analyst_task'],
			output_json=Review
		)

	@crew
	def crew(self, knowledge_source_file=None) -> Crew:

		knowledge_sources = []
		if knowledge_source_file is not None:
			with open(knowledge_source_file, 'r') as file:
				data = file.read().rstrip()

			knowledge_sources.append(
				StringKnowledgeSource(
					content=data
				)
			)

		return Crew(
			agents=self.agents,
			tasks=self.tasks,
			process=Process.sequential,
			verbose=False,
			share_crew=False,
			knowledge_sources=knowledge_sources,
		)
