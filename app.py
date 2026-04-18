from dash import Dash, html, dcc, Input, Output
import re

app = Dash(__name__)
server = app.server
app.title = "通る提案メーカー"


def normalize_text(text: str) -> str:
    if not text:
        return ""

    replacements = [
        ("無駄", "改善余地"),
        ("意味ない", "見直し余地がある"),
        ("なんで", ""),
        ("おかしい", "課題がある"),
        ("最悪", "課題が大きい"),
        ("正直", ""),
        ("と思う", ""),
        ("気がする", "傾向がある"),
    ]

    result = text
    for old, new in replacements:
        result = result.replace(old, new)

    return result.strip()


def detect_topic(text: str) -> str:
    if "会議" in text:
        return "会議の進め方"
    if "報告" in text:
        return "報告方法"
    if "工数" in text:
        return "工数管理"
    if "作業" in text or "フロー" in text:
        return "作業フロー"
    if "レビュー" in text:
        return "レビュー体制"
    return "現在の運用"


def detect_risk(topic: str) -> str:
    mapping = {
        "会議の進め方": "議論の長期化や結論の曖昧化",
        "報告方法": "認識齟齬や情報伝達のばらつき",
        "工数管理": "進捗把握の遅れや課題発見の遅延",
        "作業フロー": "工数増加や作業効率の低下",
        "レビュー体制": "品質のばらつきや待機時間の増加",
        "現在の運用": "業務効率の低下",
    }
    return mapping.get(topic, "業務効率の低下")


def build_proposal(text: str) -> str:
    cleaned = normalize_text(text)
    topic = detect_topic(cleaned)
    risk = detect_risk(topic)

    conclusion = f"{topic}には改善の余地があります。"
    background = (
        f"現在の{topic}では、{risk}が発生する可能性があります。"
        f"入力内容を見ると、「{cleaned}」という問題意識があり、現状運用に課題があると考えられます。"
    )
    proposal = (
        f"{topic}について、進め方や基準を整理し、運用方法を見直すことを提案します。"
    )
    benefit = (
        f"これにより、{risk}の抑制と、業務の進めやすさの向上が期待されます。"
    )

    return (
        f"結論：\n{conclusion}\n\n"
        f"背景・課題：\n{background}\n\n"
        f"提案内容：\n{proposal}\n\n"
        f"期待効果：\n{benefit}"
    )


def build_comments(text: str) -> list[html.Li]:
    comments = []

    if any(word in text for word in ["無駄", "意味ない", "最悪", "おかしい"]):
        comments.append(html.Li("感情の強い表現が含まれていたため、提案文では中立的な表現に変換しました。"))

    if "会議" in text:
        comments.append(html.Li("会議という対象が明確だったため、改善対象を絞って提案文を構成しました。"))
    elif "報告" in text:
        comments.append(html.Li("報告という対象が明確だったため、認識齟齬のリスクを軸に提案文を構成しました。"))
    elif "工数" in text:
        comments.append(html.Li("工数管理という対象が明確だったため、進捗把握や課題発見の遅れに置き換えました。"))
    else:
        comments.append(html.Li("対象が広めだったため、改善対象を一般化して提案文を組み立てました。"))

    comments.append(html.Li("提案が通りやすくなるよう、結論→課題→提案→期待効果の順で整理しました。"))

    return comments


app.layout = html.Div(
    [
        html.H2("通る提案メーカー"),

        html.P("違和感・不満・愚痴をそのまま入れると、上司に通りやすい提案文に整えます。"),

        dcc.Textarea(
            id="input-text",
            placeholder="例：この会議、正直無駄が多いと思う",
            style={"width": "100%", "height": 160, "fontSize": "18px"},
        ),

        html.Br(),
        html.Button("提案に変換する", id="convert-btn", n_clicks=0),

        html.H3("そのまま使える提案文"),
        dcc.Textarea(
            id="output-text",
            style={"width": "100%", "height": 320, "fontSize": "18px"},
            readOnly=True,
        ),

        html.H3("変換のポイント"),
        html.Ul(id="comment-list", style={"fontSize": "17px", "lineHeight": "1.8"}),
    ],
    style={"padding": "24px", "maxWidth": "900px", "margin": "0 auto"},
)


@app.callback(
    Output("output-text", "value"),
    Output("comment-list", "children"),
    Input("convert-btn", "n_clicks"),
    Input("input-text", "value"),
)
def convert_proposal(n_clicks, text):
    if not text:
        return "", []

    proposal = build_proposal(text)
    comments = build_comments(text)
    return proposal, comments


if __name__ == "__main__":
    app.run(debug=True)