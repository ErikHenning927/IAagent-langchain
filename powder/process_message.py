from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from databases import table_relationships, describe_tables
import re

def process_message(self, user_input):
    try:
        self.chat_history.append(("user", user_input))

        relationships = table_relationships()
        table_descriptions = describe_tables(self)

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

        decision = self.llm.invoke(context)
        reasoning = decision.content.strip()
        print(f"💭 Powder decidiu:\n{reasoning}\n")

        # 🔍 Identifica todas as tabelas mencionadas no reasoning
        mentioned_tables = [
            t for t in self.dataframes.keys()
            if re.search(rf"\b{t.lower()}\b", reasoning.lower())
        ]

        if len(mentioned_tables) > 1:
            # 🔗 Tenta encontrar relações conhecidas entre as tabelas mencionadas
            df_merged = self.dataframes[mentioned_tables[0]]
            merge_log = [mentioned_tables[0]]

            for t in mentioned_tables[1:]:
                # Procura uma chave comum entre df_merged e a próxima tabela
                common_keys = set(df_merged.columns).intersection(set(self.dataframes[t].columns))
                if common_keys:
                    key = list(common_keys)[0]
                    df_merged = df_merged.merge(self.dataframes[t], on=key, how="left")
                    merge_log.append(t)
                else:
                    print(f"⚠️ Nenhuma chave comum entre {merge_log[-1]} e {t}. Merge ignorado.")

            temp_agent = create_pandas_dataframe_agent(
                self.llm,
                df_merged,
                prefix=f"Você está trabalhando com dados combinados de {', '.join(merge_log)}.",
                agent_type=AgentType.OPENAI_FUNCTIONS,
                allow_dangerous_code=True,
                verbose=False
            )
            response = temp_agent.invoke(user_input)
            ai_response = response.get("output", "Não consegui gerar uma resposta com base nos dados combinados.")
        else:
            matched = mentioned_tables[0] if mentioned_tables else None
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