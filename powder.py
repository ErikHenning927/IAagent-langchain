import openai
from dotenv import load_dotenv, find_dotenv
import os
import pandas as pd
from langchain_openai import OpenAI, ChatOpenAI
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType

load_dotenv(find_dotenv())

client = openai.Client()


class ChatLLM():
    def __init__(self, model="gpt-4-turbo"):
        self.llm = ChatOpenAI(model=model)
        self.create_agent()
        self.chat_history = []


    def create_agent(self):
        agent_prompt_prefix = '''
        Você se chama Powder, e está trabalhando com um dataframe Pandas no Python. O nome do dataframe é df. 

        Responda de forma clara e objetiva. Se necessário, mostre código ou resultados de análises dos dados.
        '''
        
        # Verificar se o arquivo CSV existe
        csv_file = 'df_rent.csv'
        if not os.path.exists(csv_file):
            print(f"⚠️ Arquivo {csv_file} não encontrado. Criando um dataframe de exemplo...")
            # Criar um dataframe de exemplo se o arquivo não existir
            df = pd.DataFrame({
                'preco': [1500, 2000, 1200, 1800, 2200],
                'quartos': [2, 3, 1, 2, 3],
                'bairro': ['Centro', 'Batel', 'Água Verde', 'Bigorrilho', 'Batel'],
                'area': [60, 80, 45, 70, 90]
            })
            df.to_csv(csv_file, index=False)
            print(f"✅ Arquivo {csv_file} criado com dados de exemplo.")
        else:
            df = pd.read_csv(csv_file)
        
        self.agent = create_pandas_dataframe_agent(
            self.llm,
            df,
            prefix=agent_prompt_prefix,
            verbose=True,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            allow_dangerous_code=True  # Necessário para execução de código pandas
        )

    def process_message(self, user_input):
        """Processa a mensagem do usuário e retorna a resposta do agente"""
        print(f"👤 Usuário: {user_input}")
        
        try:
            # Adicionar à história do chat
            self.chat_history.append(("user", user_input))
            
            # Obter resposta do agente
            response = self.agent.invoke(user_input)
            ai_response = response.get("output", "Desculpe, não consegui processar sua solicitação.")
            
            print(f"🤖 Powder: {ai_response}")
            
            # Adicionar resposta à história
            self.chat_history.append(("ai", ai_response))
            
            return ai_response
            
        except Exception as e:
            error_msg = f"❌ Erro ao processar mensagem: {str(e)}"
            print(error_msg)
            return error_msg

    def show_commands(self):
        """Mostra os comandos disponíveis"""
        commands = """
        📋 Comandos disponíveis:
        • /help ou /h - Mostrar esta ajuda
        • /history ou /hist - Mostrar histórico da conversa
        • /clear - Limpar histórico
        • /info - Informações sobre o dataset
        • /quit ou /q - Sair do chat
        • Digite qualquer pergunta sobre os dados para análise
        
        💡 Exemplos de perguntas:
        • "Qual o preço médio dos imóveis?"
        • "Mostre os 5 imóveis mais caros"
        • "Quantos imóveis têm 2 quartos?"
        • "Faça um gráfico dos preços por bairro"
        """
        print(commands)

    def show_history(self):
        """Mostra o histórico da conversa"""
        if not self.chat_history:
            print("📝 Nenhuma conversa ainda.")
            return
        
        print("\n📝 Histórico da Conversa:")
        print("-" * 50)
        for i, (role, message) in enumerate(self.chat_history, 1):
            icon = "👤" if role == "user" else "🤖"
            name = "Usuário" if role == "user" else "Powder"
            print(f"{i}. {icon} {name}: {message[:100]}{'...' if len(message) > 100 else ''}")
        print("-" * 50)

    def show_dataset_info(self):
        """Mostra informações sobre o dataset"""
        try:
            df = pd.read_csv('df_rent.csv')
            print("\n📊 Informações do Dataset:")
            print(f"• Número de registros: {len(df)}")
            print(f"• Número de colunas: {len(df.columns)}")
            print(f"• Colunas: {', '.join(df.columns.tolist())}")
            print(f"• Primeiras 3 linhas:")
            print(df.head(3).to_string())
        except Exception as e:
            print(f"❌ Erro ao carregar informações do dataset: {e}")

    def clear_history(self):
        """Limpa o histórico da conversa"""
        self.chat_history = []
        print("🗑️ Histórico limpo!")

    def run(self):
        """Executa o loop principal do chat"""
        print("🚀 Chat LLM Agent iniciado!")
        print("👋 Olá! Eu sou a Powder, sua assistente para análise de dados.")
        print("Digite /help para ver os comandos disponíveis ou faça uma pergunta sobre os dados.")
        print("-" * 60)
        
        while True:
            try:
                # Receber input do usuário
                user_input = input("\n💬 Você: ").strip()
                
                # Verificar se é um comando
                if user_input.lower() in ['/quit', '/q']:
                    print("👋 Até logo!")
                    break
                elif user_input.lower() in ['/help', '/h']:
                    self.show_commands()
                elif user_input.lower() in ['/history', '/hist']:
                    self.show_history()
                elif user_input.lower() == '/clear':
                    self.clear_history()
                elif user_input.lower() == '/info':
                    self.show_dataset_info()
                elif user_input == '':
                    continue
                else:
                    # Processar mensagem normal
                    self.process_message(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Chat interrompido. Até logo!")
                break
            except EOFError:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    chat_llm = ChatLLM()
    chat_llm.run()