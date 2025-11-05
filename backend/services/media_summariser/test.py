from transformers import pipeline
from langchain_huggingface import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from transformers.utils.logging import set_verbosity_error

set_verbosity_error()

summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn")
summarizer = HuggingFacePipeline(pipeline=summarization_pipeline)

refinement_pipeline = pipeline("summarization", model="facebook/bart-large")
refiner = HuggingFacePipeline(pipeline=refinement_pipeline)

qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

summary_template = PromptTemplate.from_template("Summarize the following text in a :\n\n{text}")

summarization_chain = summary_template | summarizer | refiner

text_to_summarize = """(0.0, 3.84)--> I don't actually know if Christian Bale did say this, but the quote is,
(3.84, 7.04)--> if you have a problem with me, text me. And if you don't have my number,
(7.04, 10.24)--> you don't know me well enough to have a problem with me. That's so good."""
#length = input("\nEnter the length (short/medium/long): ")

summary = summarization_chain.invoke({"text": text_to_summarize})

print("\n🔹 **Generated Summary:**")
print(summary)

while True:
    question = input("\nAsk a question about the summary (or type 'exit' to stop):\n")
    if question.lower() == "exit":
        break

    qa_result = qa_pipeline(question=question, context=summary)

    print("\n🔹 **Answer:**")
    print(qa_result["answer"])
    