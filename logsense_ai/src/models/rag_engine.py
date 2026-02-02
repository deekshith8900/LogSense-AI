import logging
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from logsense_ai.src.models.vector_store import LogVectorStore

class RAGEngine:
    """
    Handles Semantic Search and Retrieval Augmented Generation (RAG).
    """
    def __init__(self, index_path="logsense_ai/data/processed/faiss_index"):
        self.logger = logging.getLogger(__name__)
        self.vector_store = LogVectorStore(index_path=index_path)
        # Load the index (must exist)
        self.vector_store.load()
        
        # Initialize LLM with OpenRouter
        # Usage depends on OPENROUTER_API_KEY being set
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
             self.logger.warning("OPENROUTER_API_KEY not found. LLM search will fail.")
        
        self.llm = ChatOpenAI(
            model_name="mistralai/mistral-7b-instruct:free", # Using a free model on OpenRouter
            temperature=0,
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1"
        )
        
        self.prompt_template = PromptTemplate(
            input_variables=["logs", "question"],
            template="""You are an expert SRE and Data Engineer assistant. 
            Analyze the following log entries to answer the user's question.
            If the logs do not contain enough information, state that clearly.
            
            Logs:
            {logs}
            
            Question: 
            {question}
            
            Analysis (Root Cause & Explanation):"""
        )

    def search(self, query, k=5):
        """
        Retrieves top-k relevant log chunks for the query.
        """
        self.logger.info(f"Searching for: {query}")
        docs = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]

    def analyze_incident(self, query, k=5):
        """
        Full RAG flow: Search -> Prompt -> Generate.
        Returns a dictionary with 'answer' and 'source_logs'.
        """
        retrieved_logs = self.search(query, k=k)
        
        if not retrieved_logs:
            return {
                "answer": "No relevant logs found to analyze this issue.",
                "source_logs": []
            }
        
        # Combine logs into a context string
        context_logs = "\n\n".join(retrieved_logs)
        
        # Format prompt
        prompt = self.prompt_template.format(logs=context_logs, question=query)
        
        self.logger.info("Generating explanation from LLM...")
        try:
            response = self.llm.invoke(prompt)
            return {
                "answer": response.content,
                "source_logs": retrieved_logs
            }
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return {
                "answer": "Error generating explanation. Please check your API Key.",
                "source_logs": retrieved_logs
            }
