from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType


def process_message(self, user_input):
    try:
        self.chat_history.append(("user", user_input))

        relationships = self.table_relationships()
        table_descriptions = self.describe_tables()

        context = f"""
        Você é a Powder, analista de dados de um e-commerce.
        Abaixo estão as tabelas disponíveis no banco e como elas se relacionam:

        {table_descriptions}

        Relações conhecidas entre as tabelas:
        {relationships}

        Use essas relações para responder perguntas de negócio.
        Se precisar cruzar dados de duas ou mais tabelas, faça isso mentalmente (como se executasse um JOIN SQL).
        Pergunta do usuário: {user_input}
        """

        # 🧩 Deixa o modelo decidir qual(is) tabela(s) usar
        decision = self.llm.invoke(context)
        reasoning = decision.content.strip()

        print(f"💭 Powder decidiu:\n{reasoning}\n")

        # 🧠 Se mencionar mais de uma tabela, combinar DataFrames manualmente
        if "paymentinfo" in reasoning.lower() and "paymentmodes" in reasoning.lower():
            df = self.dataframes["paymentInfo"].merge(
                self.dataframes["paymentModes"],
                left_on="paymentModeId",
                right_on="paymentModeId",
                how="left"
            )
            temp_agent = create_pandas_dataframe_agent(
                self.llm,
                df,
                prefix="Você está trabalhando com dados combinados de paymentInfo e paymentModes.",
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                verbose=False
            )
            response = temp_agent.invoke(user_input)
            ai_response = response.get("output", "Não consegui gerar uma resposta com base nos dados combinados.")
        else:
            # Caso use apenas uma tabela
            matched = None
            for t in self.dataframes.keys():
                if t.lower() in reasoning.lower():
                    matched = t
                    break
            if matched and matched in self.agents:
                response = self.agents[matched].invoke(user_input)
                ai_response = response.get("output", "Não consegui gerar uma resposta.")
            else:
                ai_response = (
                    "Não encontrei uma tabela relevante para responder à pergunta. "
                    f"Tabelas disponíveis: {', '.join(self.dataframes.keys())}"
                )

        print(f"🤖 Powder: {ai_response}")
        self.chat_history.append(("ai", ai_response))
        return ai_response
        
    except Exception as e:
        error_msg = f"❌ Erro ao processar mensagem: {str(e)}"
        print(error_msg)
        return error_msg