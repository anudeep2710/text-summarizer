from datetime import datetime
import logging
from typing import List, Optional, Dict, Any
from retriever.language_utils import detect_language, translate_text


class ChatManager:
    def __init__(self, documentManager, llmManager):
        """
        Initialize the ChatManager with multilingual support.
        """
        self.doc_manager = documentManager
        self.llm_manager = llmManager

        logging.info("Multilingual ChatManager initialized")

    def generate_chat_response(self, query: str, selected_docs: List[str], history: List[dict],
                             query_language: Optional[str] = None, target_language: Optional[str] = None) -> List[dict]:
        """
        Generate a chat response based on the user's query and selected documents with multilingual support.

        Args:
            query (str): The user's query.
            selected_docs (List[str]): List of selected document filenames from the dropdown.
            history (List[dict]): The chat history as a list of {'role': str, 'content': str} dictionaries.
            query_language (Optional[str]): Language code of the query. If None, it will be detected.
            target_language (Optional[str]): Language to return the response in. If None, same as query language.

        Returns:
            List[dict]: Updated chat history with the new response in 'messages' format.
        """
        # Detect query language if not provided
        if not query_language:
            query_language, lang_name = detect_language(query)
            logging.info(f"Detected query language: {lang_name} ({query_language})")

        # If target language is not specified, use query language
        if not target_language:
            target_language = query_language
        timestamp = datetime.now().strftime("%H:%M:%S")
        logging.info(f"Generating chat response for query: {query} at {timestamp}")

        # Handle empty query
        if not query:
            logging.warning("Empty query received")
            return history + [{"role": "assistant", "content": "Please enter a query."}]

        # Handle no selected documents
        if not selected_docs:
            logging.warning("No documents selected")
            return history + [{"role": "assistant", "content": "Please select at least one document."}]

        # Retrieve the top 5 chunks based on the query and selected documents
        try:
            top_k_results = self.doc_manager.retrieve_top_k(
                query,
                selected_docs,
                k=5,
                query_language=query_language,
                target_language=target_language
            )
        except Exception as e:
            logging.error(f"Error retrieving chunks: {str(e)}")
            return history + [
                {"role": "user", "content": f"{query}"},
                {"role": "assistant", "content": f"Error retrieving chunks: {str(e)}"}
            ]

        if not top_k_results:
            logging.info("No relevant chunks found")
            return history + [
                {"role": "user", "content": f"{query}"},
                {"role": "assistant", "content": "No relevant information found in the selected documents."}
            ]

        # Send the top K results to the LLM to generate a response
        try:
            llm_response, source_docs = self.llm_manager.generate_response(query, top_k_results)
        except Exception as e:
            logging.error(f"Error generating LLM response: {str(e)}")
            return history + [
                {"role": "user", "content": f"{query}"},
                {"role": "assistant", "content": f"Error generating response: {str(e)}"}
            ]

        # Format the response
        response = llm_response

        # Translate response if needed
        response_language, _ = detect_language(response)
        if target_language and response_language != target_language:
            logging.info(f"Translating response from {response_language} to {target_language}")
            original_response = response
            response = translate_text(response, target_language, response_language)
            logging.info(f"Response translated successfully")

        # Uncomment to include source docs in response (optional)
        # for i, doc in enumerate(source_docs, 1):
        #     doc_id = doc.metadata.get('doc_id', 'Unknown')
        #     filename = next((name for name, d_id in self.doc_manager.document_ids.items() if d_id == doc_id), 'Unknown')
        #     response += f"\n{i}. {filename}: {doc.page_content[:100]}..."

        logging.info("Chat response generated successfully")

        # Add language information to response
        language_info = ""
        if target_language and response_language != target_language:
            language_info = f"\n\n[Response translated from {response_language} to {target_language}]"

        # Return updated history with new user query and LLM response
        return history + [
            {"role": "user", "content": f"{query}"},
            {"role": "assistant", "content": response + language_info}
        ]

    def generate_summary(self, chunks: any, summary_type: str = "medium",
                       query_language: Optional[str] = None, target_language: Optional[str] = None) -> str:
        """
        Generate a summary of the selected documents with multilingual support.

        Args:
            chunks: Document chunks to summarize.
            summary_type (str): Type of summary ("small", "medium", "detailed").
            query_language (Optional[str]): Language code of the query. If None, it will be detected.
            target_language (Optional[str]): Language to return the summary in. If None, same as document language.

        Returns:
            str: Generated summary.

        Raises:
            ValueError: If summary_type is invalid or DocumentManager/LLM is not available.
        """
        if summary_type not in ["small", "medium", "detailed"]:
            raise ValueError("summary_type must be 'small', 'medium', or 'detailed'")

        if not chunks:
            logging.warning("No documents selected for summarization")
            return "Please select at least one document."

        # Detect document language from the first chunk
        doc_language = None
        if chunks and len(chunks) > 0 and 'text' in chunks[0]:
            doc_language, lang_name = detect_language(chunks[0]['text'])
            logging.info(f"Detected document language for summary: {lang_name} ({doc_language})")
        else:
            doc_language = 'en'  # Default to English

        # If target language is not specified, use document language
        if not target_language:
            target_language = doc_language

        # Generate summary in the document's original language
        llm_summary_response = self.llm_manager.generate_summary_v0(chunks=chunks)

        # Translate summary if needed
        if target_language and target_language != doc_language:
            logging.info(f"Translating summary from {doc_language} to {target_language}")
            original_summary = llm_summary_response
            llm_summary_response = translate_text(llm_summary_response, target_language, doc_language)

            # Add translation note
            llm_summary_response += f"\n\n[Summary translated from {doc_language} to {target_language}]"

            logging.info(f"Summary translated successfully")

        return llm_summary_response

    def generate_sample_questions(self, chunks: any, target_language: Optional[str] = None):
        """
        Generate sample questions for the document with multilingual support.

        Args:
            chunks: Document chunks to generate questions for.
            target_language (Optional[str]): Language to return the questions in.
                                            If None, same as document language.

        Returns:
            str: Generated sample questions.
        """
        # Detect document language from the first chunk
        doc_language = None
        if chunks and len(chunks) > 0 and 'text' in chunks[0]:
            doc_language, lang_name = detect_language(chunks[0]['text'])
            logging.info(f"Detected document language for questions: {lang_name} ({doc_language})")
        else:
            doc_language = 'en'  # Default to English

        # Generate questions in the document's original language
        questions = self.llm_manager.generate_questions(chunks=chunks)

        # Translate questions if needed
        if target_language and target_language != doc_language:
            logging.info(f"Translating questions from {doc_language} to {target_language}")
            questions = translate_text(questions, target_language, doc_language)
            logging.info(f"Questions translated successfully")

        return questions
