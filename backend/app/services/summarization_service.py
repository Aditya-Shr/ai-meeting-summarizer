from transformers import pipeline
import os

class SummarizationService:
    _summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    _extractor = pipeline("text2text-generation", model="google/flan-t5-base")

    @staticmethod
    def summarize_text(text: str) -> str:
        if not text or not text.strip():
            return ""
        summary = SummarizationService._summarizer(text, max_length=130, min_length=30, do_sample=False)
        return summary[0]['summary_text']

    @staticmethod
    def extract_action_items(text: str):
        prompt = (
            "Extract all action items from the following meeting transcript. "
            "List each action item as a bullet point:\n\n"
            f"{text}\n\nAction Items:"
        )
        result = SummarizationService._extractor(prompt, max_length=256, do_sample=False)
        return result[0]['generated_text']

    @staticmethod
    def extract_decisions(text: str):
        prompt = (
            "Extract all decisions made in the following meeting transcript. "
            "List each decision as a bullet point:\n\n"
            f"{text}\n\nDecisions:"
        )
        result = SummarizationService._extractor(prompt, max_length=256, do_sample=False)
        return result[0]['generated_text'] 