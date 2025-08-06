import base64
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import json
import datetime
from pathlib import Path
import textwrap

test_scores = []

def wrap_labels(labels, width=15):
    return ["\n".join(textwrap.wrap(label, width=width)) for label in labels]

def format_percent_change(current, previous):
    if previous == 0:
        return "N/A", "gray"
    delta = ((current - previous) / previous) * 100
    color = "green" if delta > 0 else "red" if delta < 0 else "gray"
    symbol = "+" if delta > 0 else ""
    return f"{symbol}{delta:.1f}%", color

def pytest_runtest_makereport(item, call):
    if call.when == "call":
        score_data = getattr(item, 'score_data', None)
        if score_data:
            test_scores.append(score_data)
            score_data["timestamp"] = datetime.datetime.now().isoformat()
            history_file = Path("test_history.jsonl")
            with history_file.open("a") as f:
                f.write(json.dumps(score_data) + "\n")

def pytest_html_results_summary(prefix, summary, postfix):
    if not test_scores:
        return

    questions = [t["question"] for t in test_scores]
    relevancy = [t["relevancy"] for t in test_scores]
    faithfulness = [t["faithfulness"] if t["faithfulness"] is not None else 0 for t in test_scores]
    bias = [t["bias"] for t in test_scores]
    hallucination = [t["hallucination"] if t["hallucination"] is not None else 0 for t in test_scores]
    rag_times = [t["rag_time_sec"] for t in test_scores]

    x = range(len(questions))
    bar_width = 0.15
    wrapped_questions = wrap_labels(questions)

    plt.figure(figsize=(14, 6))
    plt.bar([i - 1.5 * bar_width for i in x], relevancy, width=bar_width, label='Relevancy', color='skyblue')
    plt.bar([i - 0.5 * bar_width for i in x], faithfulness, width=bar_width, label='Faithfulness', color='lightgreen')
    plt.bar([i + 0.5 * bar_width for i in x], bias, width=bar_width, label='Bias', color='orange')
    plt.bar([i + 1.5 * bar_width for i in x], hallucination, width=bar_width, label='Hallucination', color='violet')
    plt.xticks(ticks=x, labels=wrapped_questions, fontsize=9)
    plt.ylabel('Score')
    plt.title('RAG Evaluation: Relevancy, Faithfulness, Bias & Hallucination')
    plt.legend()
    plt.tight_layout()

    buffer1 = BytesIO()
    plt.savefig(buffer1, format='png')
    buffer1.seek(0)
    encoded1 = base64.b64encode(buffer1.read()).decode('utf-8')
    summary.append(f'<h2>📊 RAG Evaluation: Relevancy, Faithfulness, Bias & Hallucination</h2><img src="data:image/png;base64,{encoded1}" width="900"/>')
    plt.close()

    plt.figure(figsize=(12, 4))
    plt.bar(x, rag_times, color='orange')
    plt.xticks(ticks=x, labels=wrapped_questions, fontsize=9)
    plt.ylabel('Seconds')
    plt.title('RAG Response Time per Question')
    plt.tight_layout()

    buffer2 = BytesIO()
    plt.savefig(buffer2, format='png')
    buffer2.seek(0)
    encoded2 = base64.b64encode(buffer2.read()).decode('utf-8')
    summary.append(f'<h2>⏱️ RAG Response Time</h2><img src="data:image/png;base64,{encoded2}" width="900"/>')
    plt.close()

    history_file = Path("test_history.jsonl")
    if history_file.exists():
        records = [json.loads(line) for line in history_file.read_text().splitlines()]
        df = pd.DataFrame(records)

        if not df.empty:
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            df.sort_values("timestamp", inplace=True)

            chart_html = '''
            <style>
                details.custom-dropdown summary {
                    font-size: 18px;
                    font-weight: bold;
                    background-color: #f0f0f0;
                    padding: 12px;
                    border-radius: 6px;
                    cursor: pointer;
                    margin-top: 20px;
                    outline: none;
                }
                details.custom-dropdown summary:hover {
                    background-color: #e0e0e0;
                }
            </style>
            <details class="custom-dropdown">
                <summary> Click here to view Trend Over Time Charts</summary>
            '''

            for metric in ["relevancy", "faithfulness", "bias", "hallucination", "rag_time_sec"]:
                plt.figure(figsize=(12, 4))
                for question, group in df.groupby("question"):
                    if metric in group:
                        plt.plot(group["timestamp"], group[metric], marker='o', label=question)

                if metric == "rag_time_sec":
                    plt.ylabel("RAG Response (sec)")
                    plt.title("RAG Response Trend Over Time")
                else:
                    plt.ylabel(metric.capitalize())
                    plt.title(f'{metric.capitalize()} Trend Over Time')

                ax = plt.gca()
                ax.set_xticks([])
                ax.set_xticklabels([])
                plt.tight_layout()
                plt.legend(loc='best', fontsize='small')

                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                plt.close()
                buffer.seek(0)
                encoded = base64.b64encode(buffer.read()).decode('utf-8')
                chart_html += f'<img src="data:image/png;base64,{encoded}" width="900"/>'

            chart_html += '</details>'
            summary.append(chart_html)

    if history_file.exists():
        df = pd.read_json(history_file, lines=True)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df.sort_values("timestamp", inplace=True)

        trend_rows = []
        for question, group in df.groupby("question"):
            recent = group.tail(3)
            if len(recent) >= 2:
                latest = recent.iloc[-1]
                previous = recent.iloc[-2]

                rel_delta, rel_color = format_percent_change(latest["relevancy"], previous["relevancy"])
                faith_delta, faith_color = format_percent_change(latest["faithfulness"], previous["faithfulness"])
                bias_delta, bias_color = format_percent_change(latest["bias"], previous["bias"])
                hall_delta, hall_color = format_percent_change(
                    latest["hallucination"] if latest["hallucination"] is not None else 0,
                    previous["hallucination"] if previous["hallucination"] is not None else 0
                )
                rag_delta = format_percent_change(latest["rag_time_sec"], previous["rag_time_sec"])[0]

                trend_rows.append({
                    "question": question,
                    "rel_delta": rel_delta,
                    "rel_color": rel_color,
                    "faith_delta": faith_delta,
                    "faith_color": faith_color,
                    "bias_delta": bias_delta,
                    "bias_color": bias_color,
                    "hall_delta": hall_delta,
                    "hall_color": hall_color,
                    "rag_delta": rag_delta
                })

        if trend_rows:
            html = '<h2>📈 Metric Trends (Last 3 Runs)</h2>'
            html += '<table border="1" style="border-collapse: collapse; font-size: 14px;">'
            html += '<tr><th>Question</th><th>Relevancy Δ</th><th>Faithfulness Δ</th><th>Bias Δ</th><th>Hallucination Δ</th><th>RAG Time Δ</th></tr>'
            for row in trend_rows:
                q = textwrap.shorten(row["question"], width=40, placeholder="...")
                html += (
                    f'<tr>'
                    f'<td>{q}</td>'
                    f'<td style="color:{row["rel_color"]}">{row["rel_delta"]}</td>'
                    f'<td style="color:{row["faith_color"]}">{row["faith_delta"]}</td>'
                    f'<td style="color:{row["bias_color"]}">{row["bias_delta"]}</td>'
                    f'<td style="color:{row["hall_color"]}">{row["hall_delta"]}</td>'
                    f'<td>{row["rag_delta"]}</td>'
                    f'</tr>'
                )
            html += '</table>'
            summary.append(html)
