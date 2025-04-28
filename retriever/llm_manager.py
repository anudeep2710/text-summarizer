import logging
import os
from typing import List, Dict, Any, Tuple
from langchain_groq import ChatGroq
from langchain.chains import RetrievalQA
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

class LLMManager:
    DEFAULT_MODEL = "gemma2-9b-it"  # Set the default model name

    def __init__(self):
        self.generation_llm = None
        logging.info("LLMManager initialized")

        # Initialize the default model during construction
        try:
            self.initialize_generation_llm(self.DEFAULT_MODEL)
            logging.info(f"Initialized default LLM model: {self.DEFAULT_MODEL}")
        except ValueError as e:
            logging.error(f"Failed to initialize default LLM model: {str(e)}")

    def initialize_generation_llm(self, model_name: str) -> None:
        """
        Initialize the generation LLM using the Groq API.

        Args:
            model_name (str): The name of the model to use for generation.

        Raises:
            ValueError: If GROQ_API_KEY is not set.
        """
        # Try to get API key from environment
        api_key = os.getenv("GROQ_API_KEY")
        
        # If not found, try to load from .env file as a fallback
        if not api_key:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                api_key = os.getenv("GROQ_API_KEY")
                logging.info("Loaded API key from .env file")
            except ImportError:
                logging.warning("python-dotenv not installed. Cannot load from .env file.")
            except Exception as e:
                logging.warning(f"Error loading from .env file: {str(e)}")
        
        # If still not found, raise error
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set. Please add it in your environment variables or .env file.")
        
        # Set it in the environment explicitly
        os.environ["GROQ_API_KEY"] = api_key
        
        # Create the ChatGroq instance with proper configuration
        try:
            self.generation_llm = ChatGroq(
                model=model_name,  # Parameter is 'model', not 'model_name'
                temperature=0.7,
                api_key=api_key    # Parameter is 'api_key', not 'groq_api_key'
            )
            self.generation_llm.name = model_name
            logging.info(f"Generation LLM {model_name} initialized successfully")
        except Exception as e:
            logging.error(f"Error initializing ChatGroq: {str(e)}")
            raise ValueError(f"Failed to initialize ChatGroq: {str(e)}")
            
        # Test if the LLM is working
        if not self.generation_llm:
            raise ValueError("LLM initialization failed - the instance is None")

    def reinitialize_llm(self, model_name: str) -> str:
        """
        Reinitialize the LLM with a new model name.

        Args:
            model_name (str): The name of the new model to initialize.

        Returns:
            str: Status message indicating success or failure.
        """
        try:
            self.initialize_generation_llm(model_name)
            return f"LLM model changed to {model_name}"
        except ValueError as e:
            logging.error(f"Failed to reinitialize LLM with model {model_name}: {str(e)}")
            return f"Error: Failed to change LLM model: {str(e)}"

    def generate_response(self, question: str, relevant_docs: List[Dict[str, Any]]) -> Tuple[str, List[Document]]:
        """
        Generate a response using the generation LLM based on the question and relevant documents.

        Args:
            question (str): The user's query.
            relevant_docs (List[Dict[str, Any]]): List of relevant document chunks with text, metadata, and scores.

        Returns:
            Tuple[str, List[Document]]: The LLM's response and the source documents used.

        Raises:
            ValueError: If the generation LLM is not initialized.
            Exception: If there's an error during the QA chain invocation.
        """
        if not self.generation_llm:
            raise ValueError("Generation LLM is not initialized. Call initialize_generation_llm first.")

        # Convert the relevant documents into LangChain Document objects
        documents = [
            Document(page_content=doc['text'], metadata=doc['metadata'])
            for doc in relevant_docs
        ]

        # Create a proper retriever by subclassing BaseRetriever
        class SimpleRetriever(BaseRetriever):
            def __init__(self, docs: List[Document], **kwargs):
                super().__init__(**kwargs)  # Pass kwargs to BaseRetriever
                self._docs = docs  # Use a private attribute to store docs
                logging.debug(f"SimpleRetriever initialized with {len(docs)} documents")

            def _get_relevant_documents(self, query: str) -> List[Document]:
                logging.debug(f"SimpleRetriever._get_relevant_documents called with query: {query}")
                return self._docs

            async def _aget_relevant_documents(self, query: str) -> List[Document]:
                logging.debug(f"SimpleRetriever._aget_relevant_documents called with query: {query}")
                return self._docs

        # Instantiate the retriever
        retriever = SimpleRetriever(docs=documents)

        # Create a retrieval-based question-answering chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.generation_llm,
            retriever=retriever,
            return_source_documents=True
        )

        try:
            result = qa_chain.invoke({"query": question})
            response = result['result']
            source_docs = result['source_documents']
            #logging.info(f"Generated response for question: {question} : {response}")
            return response, source_docs
        except Exception as e:
            logging.error(f"Error during QA chain invocation: {str(e)}")
            raise e

    def generate_summary_v0(self, chunks: any):
        logging.info("Generating summary ...")
        
        # Limit the number of chunks (for example, top 30 chunks)
        limited_chunks = chunks[:30]
        
        # Combine text from the selected chunks
        full_text = "\n".join(chunk['text'] for chunk in limited_chunks)
        text_length = len(full_text)
        logging.info(f"Total text length (characters): {text_length}")
        
        # Define a maximum character limit to fit in a 1024-token context.
        # For many models, roughly 3200 characters is a safe limit.
        MAX_CHAR_LIMIT = 3200
        if text_length > MAX_CHAR_LIMIT:
            logging.warning(f"Input text too long ({text_length} chars), truncating to {MAX_CHAR_LIMIT} chars.")
            full_text = full_text[:MAX_CHAR_LIMIT]
        
        # Define a custom prompt to instruct concise summarization in bullet points.
        custom_prompt_template = """
            You are an expert summarizer. Summarize the following text into a concise summary using bullet points.
            Ensure that the final summary is no longer than 20-30 bullet points and fits within 15-20 lines.
            Focus only on the most critical points.

            Text to summarize:
            {text}

            Summary:
            """
        prompt = PromptTemplate(input_variables=["text"], template=custom_prompt_template)
        
        # Use the 'stuff' chain type to send a single LLM request with our custom prompt.
        chain = load_summarize_chain(self.generation_llm, chain_type="stuff", prompt=prompt)
        
        # Wrap the full text in a single Document object (chain expects a list of Documents)
        docs = [Document(page_content=full_text)]
        
        # Generate the summary
        summary = chain.invoke(docs)
        return summary['output_text']
    
    def generate_questions(self, chunks: any):
        logging.info("Generating sample questions ...")
        
        # Use the top 30 chunks or fewer
        limited_chunks = chunks[:30]
        
        # Combine text from chunks
        full_text = "\n".join(chunk['text'] for chunk in limited_chunks)
        text_length = len(full_text)
        logging.info(f"Total text length for questions: {text_length}")
        
        MAX_CHAR_LIMIT = 3200
        if text_length > MAX_CHAR_LIMIT:
            logging.warning(f"Input text too long ({text_length} chars), truncating to {MAX_CHAR_LIMIT} chars.")
            full_text = full_text[:MAX_CHAR_LIMIT]
        
        # Prompt template for generating questions
        question_prompt_template = """
        You are an AI expert at creating questions from documents.

        Based on the text below, generate not less than 20 insightful and highly relevant sample questions that a user might ask to better understand the content.

        **Instructions:**
        - Questions must be specific to the document's content and context.
        - Avoid generic questions like 'What is this document about?'
        - Do not include numbers, prefixes (e.g., '1.', '2.'), or explanations (e.g., '(Clarifies...)').
        - Each question should be a single, clear sentence ending with a question mark.
        - Focus on key concepts, processes, components, or use cases mentioned in the text.

        Text:
        {text}

        Output format:
        What is the purpose of the Communication Server in Collateral Management?
        How does the system handle data encryption for secure communication?
        ...
        """
        prompt = PromptTemplate(input_variables=["text"], template=question_prompt_template)
        
        chain = load_summarize_chain(self.generation_llm, chain_type="stuff", prompt=prompt)
        docs = [Document(page_content=full_text)]

        try:
            result = chain.invoke(docs)
            question_output = result.get("output_text", "").strip()
            
            # Clean and parse the output into a list of questions
            questions = []
            for line in question_output.split("\n"):
                # Remove any leading/trailing whitespace, numbers, or bullet points
                cleaned_line = line.strip().strip("-*1234567890. ").rstrip(".")
                # Remove any explanation in parentheses
                cleaned_line = cleaned_line.split("(")[0].strip()
                # Ensure the line is a valid question (ends with '?' and is not empty)
                if cleaned_line and cleaned_line.endswith("?"):
                    questions.append(cleaned_line)
            
            # Limit to 10 questions
            questions = questions[:10]
            logging.info(f"Generated questions: {questions}")
            return questions
        except Exception as e:
            logging.error(f"Error generating questions: {e}")
            return []
    
    def generate_summary(self, chunks: Any, toc_text: Any = None, summary_type: str = "medium") -> str:
        """
        Generate a summary of the document using LangChain's summarization chains.

        Args:
            chunks: Document chunks to summarize
            toc_text: Table of contents (if available)
            summary_type (str): Type of summary ("small", "medium", "detailed")

        Returns:
            str: Generated summary.
        """
        logging.info(f"Generating {summary_type} summary")
        
        # Check if LLM is initialized properly
        if not self.generation_llm:
            logging.error("LLM is not initialized. Cannot generate summary.")
            return "Error: LLM is not initialized. Please check the API key configuration."
        
        # Define word count based on summary type
        if summary_type == "small":
            word_count = "50-100"
        elif summary_type == "medium":
            word_count = "200-400"
        else:  # detailed
            word_count = "500-1000"
            
        # Limit the number of chunks based on summary type
        if summary_type == "small":
            limited_chunks = chunks[:5]
        elif summary_type == "medium":
            limited_chunks = chunks[:15]
        else:  # detailed
            limited_chunks = chunks[:30]
            
        # Combine text from the selected chunks
        full_text = "\n".join(chunk['text'] for chunk in limited_chunks)
        text_length = len(full_text)
        logging.info(f"Total text length (characters): {text_length}")
        
        # Define a maximum character limit
        MAX_CHAR_LIMIT = 4000
        if text_length > MAX_CHAR_LIMIT:
            logging.warning(f"Input text too long ({text_length} chars), truncating to {MAX_CHAR_LIMIT} chars.")
            full_text = full_text[:MAX_CHAR_LIMIT]
        
        # Create the TOC section if available
        toc_section = ""
        if toc_text:
            toc_section = "Table of Contents:\n" + str(toc_text) + "\n\n"
        
        # Create prompt with no f-strings, using PromptTemplate directly
        template = (
            "Generate a {summary_type} summary ({word_count} words) of the following document.\n"
            "Focus on key points and ensure clarity. Stick strictly to the provided text.\n\n"
            "{toc_section}\n"
            "Document:\n"
            "{text}\n\n"
            "Summary:"
        )
        
        try:
            # Use direct runnable syntax
            prompt = PromptTemplate.from_template(template)
            chain = prompt | self.generation_llm | StrOutputParser()
            
            # Invoke with all the parameters
            summary = chain.invoke({
                "summary_type": summary_type,
                "word_count": word_count,
                "toc_section": toc_section,
                "text": full_text
            })
            
            logging.info(f"{summary_type.capitalize()} summary generated successfully")
            return summary
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            return f"Error generating summary: {str(e)}"