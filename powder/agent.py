import openai
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
client = openai.Client()

def create_agent(self):
    agent_prompt_prefix = """
    Você se chama Powder, e é um analista de dados especialista em e-commerce.
    Você tem acesso a múltiplas tabelas do banco de dados (clientes, pedidos, produtos, etc.).
    Responda perguntas sobre vendas, clientes e produtos usando os dados disponíveis.
    Quando necessário, combine dados de múltiplas tabelas (por exemplo, pedidos + clientes).
    """

    # Cria um agente para cada tabela
    self.agents = {
        name: create_pandas_dataframe_agent(
            self.llm,
            df,
            prefix=agent_prompt_prefix + f"\nTabela: {name}",
            verbose=False,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True,
        )
        for name, df in self.dataframes.items()
    }