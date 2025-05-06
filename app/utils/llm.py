from typing import List

from langchain import OpenAI
from langchain.agents import AgentExecutor, AgentOutputParser, LLMSingleActionAgent
from langchain.chains.llm import LLMChain
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentFinish

from app.core.config import settings

# Prompt Template
template = """Answer the following question as best you can, using the text chunks provided below:

Text Chunks: {text_chunks}

Question: {input}

Begin! The answer should very detailed: 
{agent_scratchpad}"""


def documents_agent(text_chunks: str, question: str) -> str:
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=[], verbose=True
    )
    answer = agent_executor.run(task=question, text_chunks=text_chunks, input=question)
    return answer


class CustomPromptTemplate(StringPromptTemplate):
    template: str
    input_variables: List[str] = ["input", "intermediate_steps", "text_chunks"]

    def format(self, **kwargs) -> str:
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        kwargs["agent_scratchpad"] = thoughts
        return self.template.format(**kwargs)


# Initialize prompt templating
prompt = CustomPromptTemplate(
    template=template, input_variables=["input", "intermediate_steps", "text_chunks"]
)


class CustomOutputParser(AgentOutputParser):
    @staticmethod
    def parse(llm_output: str) -> AgentFinish:
        if "Final Answer:" in llm_output:
            return AgentFinish(
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        else:
            return AgentFinish(
                return_values={"output": llm_output.strip()},
                log=llm_output,
            )


# Initialize output parser
output_parser = CustomOutputParser()

llm = OpenAI(temperature=0, openai_api_key=settings.OPENAI_API_KEY)

# LLM chain consisting of the LLM and a prompt
llm_chain = LLMChain(llm=llm, prompt=prompt)

# Define the agent
agent = LLMSingleActionAgent(
    llm_chain=llm_chain, output_parser=output_parser, stop=["<|END|>"], allowed_tools=[]
)
