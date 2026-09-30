from langchain_ollama import ChatOllama

class LLMManager:
    def __init__(self,model_name:str="qwen3:4b"):
        self.model_name=model_name
        self.llm=ChatOllama(model=model_name)

    def generate_response(self,prompt:str)->str:
        response=self.llm.invoke(prompt)
        return response.content


if __name__ == "__main__":
    llm_manager = LLMManager()

    prompt = "What is an HR policy? Explain in two sentences."

    response = llm_manager.generate_response(prompt)

    print("\nLLM Response:")
    print(response)