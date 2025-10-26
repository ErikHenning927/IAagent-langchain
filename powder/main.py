from langchain_openai import ChatOpenAI
from agent import *
from databases import *
from process_message import *



class ChatLLM:
    def __init__(self, model="gpt-4-turbo"):
        self.llm = ChatOpenAI(model=model)
        self.chat_history = []
        self.dataframes = load_all_tables_from_db()
        create_agent(self)

    def run(self):
        print("Agent Powder conectado ao banco! 💬")
        print("-" * 60)

        while True:
            try:
                user_input = input("\nPergunte a Powder: ").strip()
                if user_input.lower() in ["sair", "exit", "quit"]:
                    print("\n👋 Encerrando chat. Até logo!")
                    break
                self.process_message(user_input)

            except KeyboardInterrupt:
                print("\n\n👋 Chat interrompido. Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {e}")

if __name__ == "__main__":
    chat_llm = ChatLLM()
    chat_llm.run()
