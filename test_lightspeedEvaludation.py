import pytest
import time
from Utils.rag_respose import get_rag_response
from Utils.prompt_contexts import get_context, get_all_questions 
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    BiasMetric
)
from deepeval.test_case import LLMTestCase

# Dynamically load questions from context
QUESTIONS = get_all_questions()


@pytest.mark.parametrize("question", QUESTIONS)
def test_llm_quality(question, request):
    print("\n" + "=" * 100)
    print(f"🚀 Testing question: {question}")

    start_time = time.time()
    response, rag_time = get_rag_response(question)

    if rag_time == 0.0:
        pytest.skip(f"RAG response failed: {response}")

    print(f"\n📥 Model Response:\n{response}")

    context_retrieved = get_context(question)
    if not context_retrieved:
        print("\n⚠️ No context retrieved. Skipping faithfulness and hallucination metrics.\n")
        context_retrieved = None
    else:
        print(f"\n📚 Context Retrieved:\n{context_retrieved}")

    test_case = LLMTestCase(
        input=question,
        actual_output=response,
        context=context_retrieved,
        retrieval_context=context_retrieved
    )

    # Always evaluate these metrics
    relevancy = AnswerRelevancyMetric(include_reason=True)
    bias = BiasMetric(include_reason=True)

    relevancy.measure(test_case)
    bias.measure(test_case)

    # Conditionally evaluate Faithfulness & Hallucination
    faithfulness_score = None
    faithfulness_reason = "No retrieval context available."
    hallucination_score = None
    hallucination_reason = "No context available."

    if context_retrieved:
        faithfulness = FaithfulnessMetric(include_reason=True)
        faithfulness.measure(test_case)
        faithfulness_score = faithfulness.score
        faithfulness_reason = faithfulness.reason

        hallucination = HallucinationMetric(include_reason=True)
        hallucination.measure(test_case)
        hallucination_score = hallucination.score
        hallucination_reason = hallucination.reason

    duration = time.time() - start_time

    # Print scores
    print(f"\n✅ Relevancy Score: {relevancy.score}")
    print(f"💬 Relevancy Reason: {relevancy.reason}")

    print(f"\n⚖️ Bias Score: {bias.score}")
    print(f"🧾 Bias Reason: {bias.reason}")

    print(f"\n🧠 Faithfulness Score: {faithfulness_score}")
    print(f"🔍 Faithfulness Reason: {faithfulness_reason}")

    print(f"\n🚨 Hallucination Score: {hallucination_score}")
    print(f"📌 Hallucination Reason: {hallucination_reason}")

    print(f"⏱ Duration: {duration:.2f} seconds")
    print("=" * 100 + "\n")

    # Save results to report
    request.node.score_data = {
        "question": question,
        "relevancy": float(relevancy.score),
        "bias": float(bias.score),
        "faithfulness": float(faithfulness_score) if faithfulness_score is not None else None,
        "hallucination": float(hallucination_score) if hallucination_score is not None else None,
        "rag_time_sec": rag_time,
        "duration_sec": round(duration, 2)
    }

    # Assertions
    assert relevancy.is_successful(), f"Relevancy Test Failed: {relevancy.score} (Reason: {relevancy.reason})"
    assert bias.is_successful(), f"Bias Test Failed: {bias.score} (Reason: {bias.reason})"

    if context_retrieved:
        assert faithfulness.is_successful(), f"Faithfulness Test Failed: {faithfulness.score} (Reason: {faithfulness.reason})"
        assert hallucination.is_successful(), f"Hallucination Test Failed: {hallucination.score} (Reason: {hallucination.reason})"
