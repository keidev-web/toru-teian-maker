from dash import Dash, html, dcc, Input, Output
import re

app = Dash(__name__)
server = app.server
app.title = "通る提案メーカー"


TOPIC_RULES = {
    "トイレ": {
        "label": "トイレ備品",
        "problem_map": {
            "古い": "老朽化が進んでいる",
            "汚い": "衛生面に課題がある",
            "臭い": "衛生環境に懸念がある",
            "使いにくい": "使用感に課題がある",
        },
        "proposal": "備品の更新を行う",
        "benefit": "衛生面と利用者の快適性の向上",
    },
    "スリッパ": {
        "label": "トイレのスリッパ",
        "problem_map": {
            "古い": "老朽化が進んでいる",
            "汚い": "衛生面に課題がある",
            "使いにくい": "使用感に課題がある",
        },
        "proposal": "新しいスリッパへ更新する",
        "benefit": "衛生面の改善と利用者の快適性向上",
    },
    "会議": {
        "label": "会議の進め方",
        "problem_map": {
            "長い": "会議時間が長期化している",
            "無駄": "時間効率に改善余地がある",
            "曖昧": "結論や決定事項が曖昧になりやすい",
            "広がりすぎ": "議論が拡散しやすい",
        },
        "proposal": "議題設定や進行方法を見直す",
        "benefit": "意思決定の迅速化と会議時間の短縮",
    },
    "報告": {
        "label": "報告方法",
        "problem_map": {
            "バラバラ": "報告内容や粒度にばらつきがある",
            "分かりにくい": "情報が整理されず理解しにくい",
            "遅い": "情報共有のタイミングに課題がある",
        },
        "proposal": "報告フォーマットやルールを統一する",
        "benefit": "認識齟齬の削減と確認効率の向上",
    },
    "工数": {
        "label": "工数管理",
        "problem_map": {
            "見えない": "進捗把握がしにくい",
            "遅れ": "課題発見が遅れやすい",
            "バラバラ": "管理方法にばらつきがある",
        },
        "proposal": "管理方法や共有ルールを見直す",
        "benefit": "進捗把握の精度向上と課題発見の早期化",
    },
    "レビュー": {
        "label": "レビュー体制",
        "problem_map": {
            "遅い": "レビュー待ち時間が長い",
            "偏る": "属人化が起きている",
            "ばらつく": "品質判断にばらつきがある",
        },
        "proposal": "レビュー基準や担当の分散方法を見直す",
        "benefit": "品質安定化と待機時間の短縮",
    },
    "備品": {
        "label": "備品運用",
        "problem_map": {
            "古い": "備品の老朽化が進んでいる",
            "足りない": "必要な備品が不足している",
            "使いにくい": "使用感に課題がある",
        },
        "proposal": "備品の更新や補充ルールを見直す",
        "benefit": "業務環境の改善と利便性向上",
    },
}

NEGATIVE_WORDS = [
    "無駄",
    "意味ない",
    "最悪",
    "イライラする",
    "腹立つ",
    "だるい",
    "しんどい",
]

DESIRE_PATTERNS = [
    ("買い替え", "更新"),
    ("変えたほうがいい", "見直し"),
    ("直したほうがいい", "改善"),
    ("やめたほうがいい", "見直し"),
    ("減らしたほうがいい", "削減"),
    ("増やしたほうがいい", "拡充"),
]


def clean_text(text: str) -> str:
    t = text.strip()
    t = t.replace("です。", "。").replace("ます。", "。")
    return t


def detect_topic(text: str) -> str:
    for key in TOPIC_RULES.keys():
        if key in text:
            return key
    return ""


def detect_problem_phrase(text: str, topic_key: str) -> str:
    if topic_key and topic_key in TOPIC_RULES:
        for word, phrase in TOPIC_RULES[topic_key]["problem_map"].items():
            if word in text:
                return phrase

    if "古い" in text:
        return "老朽化が進んでいる"
    if "汚い" in text:
        return "衛生面に課題がある"
    if "分かりにくい" in text:
        return "内容が理解しにくい"
    if "曖昧" in text:
        return "判断基準や結論が曖昧になりやすい"
    if "遅い" in text:
        return "対応や共有に時間がかかっている"
    if "バラバラ" in text:
        return "運用方法にばらつきがある"

    if any(word in text for word in NEGATIVE_WORDS):
        return "現状の運用に改善余地がある"

    return "現状の運用に課題がある"


def detect_desired_action(text: str) -> str:
    for src, dst in DESIRE_PATTERNS:
        if src in text:
            return dst
    if "買い替え" in text:
        return "更新"
    if "統一" in text:
        return "統一"
    if "可視化" in text:
        return "可視化"
    return ""


def build_topic_specific_proposal(topic_key: str, desired_action: str) -> str:
    if topic_key and topic_key in TOPIC_RULES:
        base = TOPIC_RULES[topic_key]["proposal"]
        if desired_action:
            return f"{TOPIC_RULES[topic_key]['label']}について、{desired_action}を含む形で{base}ことを提案します。"
        return f"{TOPIC_RULES[topic_key]['label']}について、{base}ことを提案します。"

    if desired_action:
        return f"現在の運用について、{desired_action}を含む形で見直しを行うことを提案します。"
    return "現在の運用について、進め方や基準を整理し、見直しを行うことを提案します。"


def build_benefit(topic_key: str) -> str:
    if topic_key and topic_key in TOPIC_RULES:
        return TOPIC_RULES[topic_key]["benefit"]
    return "業務効率や運用品質の向上"


def build_conclusion(topic_key: str, desired_action: str) -> str:
    if topic_key and topic_key in TOPIC_RULES:
        label = TOPIC_RULES[topic_key]["label"]
        if desired_action == "更新":
            return f"{label}については、更新を検討すべきです。"
        if desired_action == "統一":
            return f"{label}については、運用の統一を検討すべきです。"
        if desired_action == "可視化":
            return f"{label}については、可視化を進めるべきです。"
        return f"{label}には改善の余地があります。"
    return "現在の運用には改善の余地があります。"


def summarize_input_as_issue(text: str, topic_key: str) -> str:
    topic_label = TOPIC_RULES[topic_key]["label"] if topic_key in TOPIC_RULES else "現状の運用"
    problem_phrase = detect_problem_phrase(text, topic_key)
    return f"{topic_label}では、{problem_phrase}と考えられます。"


def build_proposal(text: str) -> str:
    cleaned = clean_text(text)
    topic_key = detect_topic(cleaned)
    desired_action = detect_desired_action(cleaned)
    conclusion = build_conclusion(topic_key, desired_action)
    issue_summary = summarize_input_as_issue(cleaned, topic_key)
    proposal = build_topic_specific_proposal(topic_key, desired_action)
    benefit = build_benefit(topic_key)

    topic_label = TOPIC_RULES[topic_key]["label"] if topic_key in TOPIC_RULES else "現在の運用"

    background = (
        f"{issue_summary} "
        f"入力内容からは「{cleaned}」という問題意識があり、"
        f"{topic_label}に関して改善ニーズがあると考えられます。"
    )

    benefit_text = f"これにより、{benefit}が期待されます。"

    return (
        f"結論：\n{conclusion}\n\n"
        f"背景・課題：\n{background}\n\n"
        f"提案内容：\n{proposal}\n\n"
        f"期待効果：\n{benefit_text}"
    )


def build_comments(text: str) -> list[html.Li]:
    comments = []
    topic_key = detect_topic(text)
    desired_action = detect_desired_action(text)

    if topic_key:
        comments.append(html.Li(f"入力文から対象として「{TOPIC_RULES[topic_key]['label']}」を抽出しました。"))
    else:
        comments.append(html.Li("対象が広めだったため、提案対象を一般化して構成しました。"))

    if desired_action:
        comments.append(html.Li(f"入力文に含まれる要望をもとに、「{desired_action}」の方向で提案内容を組み立てました。"))
    else:
        comments.append(html.Li("要望が明示されていなかったため、見直し提案として再構成しました。"))

    if any(word in text for word in NEGATIVE_WORDS):
        comments.append(html.Li("感情の強い表現は避け、上司に出しやすい中立的な表現へ変換しました。"))

    comments.append(html.Li("結論→背景・課題→提案内容→期待効果の順に整理しました。"))
    return comments


app.layout = html.Div(
    [
        html.H1("通る提案メーカー"),
        html.P("違和感・不満・愚痴をそのまま入れると、上司に通りやすい提案文に整えます。"),
        dcc.Textarea(
            id="input-text",
            placeholder="例：この会議、正直無駄が多いと思う",
            style={"width": "100%", "height": 180, "fontSize": "18px"},
        ),
        html.Br(),
        html.Button("提案に変換する", id="convert-btn"),
        html.H2("そのまま使える提案文"),
        dcc.Textarea(
            id="output-text",
            style={"width": "100%", "height": 320, "fontSize": "18px"},
            readOnly=True,
        ),
        html.H2("変換のポイント"),
        html.Ul(id="comment-list", style={"fontSize": "17px", "lineHeight": "1.8"}),
    ],
    style={"padding": "24px", "maxWidth": "960px", "margin": "0 auto"},
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