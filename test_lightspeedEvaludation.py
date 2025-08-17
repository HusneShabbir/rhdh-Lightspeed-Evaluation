import pytest
import time
import re
import os
from dotenv import load_dotenv
from playwright.sync_api import Page
from Utils.rag_respose import get_rag_response
from Utils.prompt_contexts import get_context, get_all_questions 
from Utils.auth_token import replace_auth_token
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    HallucinationMetric,
    BiasMetric,
    GEval
)
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

load_dotenv()
ENABLE_GEVAL = os.getenv("ENABLE_GENERAL_EVAL_METRICS", "no").lower() == "yes"
base_url = os.getenv('Base_Url')
expected_url = "http://localhost:7007/api/lightspeed"

# Dynamically load questions
QUESTIONS = get_all_questions()

# GEval metrics
informativeness = GEval(
    name="Informativeness",
    evaluation_steps=[
        "Does the response provide sufficient and useful information?",
        "Does the response go beyond generic statements and provide depth?"
    ],
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
)

clarity = GEval(
    name="Clarity",
    evaluation_steps=[
        "Is the response written in a clear and understandable manner?",
        "Are technical or complex ideas explained in a way the target user can follow?"
    ],
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
)

completeness = GEval(
    name="Completeness",
    evaluation_steps=[
        "Does the response address all relevant aspects of the question?",
        "Is any significant part of the question left unanswered?"
    ],
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
)

tone_appropriateness = GEval(
    name="Tone Appropriateness",
    evaluation_steps=[
        "Is the tone of the response suitable for the context?",
        "Is the language professional, empathetic, or neutral as appropriate?"
    ],
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
)

glitch_detection = GEval(
    name="Output Glitch Check",
    evaluation_steps=[
        "Does the response contain obvious generation errors such as repeated characters or words?",
        "Are there any unnatural patterns like 'loooooooong' words or random casing like 'cCCCCCCCCCCCCell'?",
        "Is the text free from typing artifacts or output noise?"
    ],
    evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT]
)

@pytest.mark.parametrize("question", QUESTIONS)
def test_llm_quality(page: Page, question, request):
    if base_url == expected_url:
        replace_auth_token(page)
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

    # Core metrics
    relevancy = AnswerRelevancyMetric(include_reason=True)
    bias = BiasMetric(include_reason=True)
    relevancy.measure(test_case)
    bias.measure(test_case)

    faithfulness_score = hallucination_score = None
    faithfulness_reason = hallucination_reason = "No context available."

    if context_retrieved:
        faithfulness = FaithfulnessMetric(include_reason=True)
        hallucination = HallucinationMetric(include_reason=True)
        faithfulness.measure(test_case)
        hallucination.measure(test_case)
        faithfulness_score = faithfulness.score
        faithfulness_reason = faithfulness.reason
        hallucination_score = hallucination.score
        hallucination_reason = hallucination.reason

    # GEval metrics (optional, based on env)
    if ENABLE_GEVAL:
        informativeness.measure(test_case)
        clarity.measure(test_case)
        completeness.measure(test_case)
        tone_appropriateness.measure(test_case)
        glitch_detection.measure(test_case)

        print(f"\n🧼 Clarity Score: {clarity.score}")
        print(f"🔍 Clarity Reason: {clarity.reason}")

        print(f"\n🔎 Informativeness Score: {informativeness.score}")
        print(f"📝 Informativeness Reason: {informativeness.reason}")

        print(f"\n📋 Completeness Score: {completeness.score}")
        print(f"✅ Completeness Reason: {completeness.reason}")

        print(f"\n🎯 Tone Appropriateness Score: {tone_appropriateness.score}")
        print(f"🗣️ Tone Appropriateness Reason: {tone_appropriateness.reason}")

        print(f"\n⚠️ Output Glitch Score: {glitch_detection.score}")
        print(f"🧪 Output Glitch Reason: {glitch_detection.reason}")

    duration = time.time() - start_time

    # Print core metric scores
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

    # Save results to request context
    request.node.score_data = {
        "question": question,
        "relevancy": float(relevancy.score),
        "bias": float(bias.score),
        "faithfulness": float(faithfulness_score) if faithfulness_score is not None else None,
        "hallucination": float(hallucination_score) if hallucination_score is not None else None,
        "informativeness": float(informativeness.score) if ENABLE_GEVAL else None,
        "clarity": float(clarity.score) if ENABLE_GEVAL else None,
        "completeness": float(completeness.score) if ENABLE_GEVAL else None,
        "tone_appropriateness": float(tone_appropriateness.score) if ENABLE_GEVAL else None,
        "glitch_check": float(glitch_detection.score) if ENABLE_GEVAL else None,
        "rag_time_sec": rag_time,
        "duration_sec": round(duration, 2)
    }

    # Assertions
    assert relevancy.is_successful(), f"Relevancy Test Failed: {relevancy.score} (Reason: {relevancy.reason})"
    assert bias.is_successful(), f"Bias Test Failed: {bias.score} (Reason: {bias.reason})"

    if ENABLE_GEVAL:
        assert informativeness.is_successful(), f"Informativeness Test Failed: {informativeness.score} (Reason: {informativeness.reason})"
        assert clarity.is_successful(), f"Clarity Test Failed: {clarity.score} (Reason: {clarity.reason})"
        assert completeness.is_successful(), f"Completeness Test Failed: {completeness.score} (Reason: {completeness.reason})"
        assert tone_appropriateness.is_successful(), f"Tone Appropriateness Test Failed: {tone_appropriateness.score} (Reason: {tone_appropriateness.reason})"
        assert glitch_detection.is_successful(), f"Glitch Test Failed: {glitch_detection.score} (Reason: {glitch_detection.reason})"

    if context_retrieved:
        assert faithfulness.is_successful(), f"Faithfulness Test Failed: {faithfulness_score} (Reason: {faithfulness_reason})"
        assert hallucination.is_successful(), f"Hallucination Test Failed: {hallucination_score} (Reason: {hallucination_reason})"
