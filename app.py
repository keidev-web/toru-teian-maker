from dash import Dash, html, dcc, Input, Output

app = Dash(__name__)
server = app.server
app.title = "通る提案メーカー"


CATEGORY_RULES = {
    "承認": {
        "topic_keywords": ["承認", "回覧", "レビュー", "コメント", "確認", "決裁"],
        "topic_label": "承認・レビュー運用",
        "problem_rules": [
            {
                "keywords": ["コメント", "なし", "承認"],
                "problem_label": "コメントがないまま承認されている",
                "business_issue": "レビューが形骸化している可能性があります",
                "proposal": "承認時のコメント記入ルールを明確化する",
                "benefit": "レビューの実効性向上と文書品質の安定化",
            },
            {
                "keywords": ["承認", "遅い"],
                "problem_label": "承認に時間がかかっている",
                "business_issue": "意思決定や進行に遅れが生じている可能性があります",
                "proposal": "承認フローや担当分担を見直す",
                "benefit": "意思決定の迅速化と待機時間の削減",
            },
            {
                "keywords": ["確認", "していない"],
                "problem_label": "十分な確認が行われていない",
                "business_issue": "承認プロセスの品質が担保されにくい状態です",
                "proposal": "確認観点を明文化し、レビュー基準を共有する",
                "benefit": "確認品質の向上と手戻りの削減",
            },
        ],
        "fallback_problem": "承認・レビュー運用に課題がある",
        "fallback_issue": "レビューの実効性や運用効率に改善余地があります",
        "fallback_proposal": "承認・レビューの進め方や基準を見直す",
        "fallback_benefit": "運用品質の向上と確認効率の改善",
    },
    "会議": {
        "topic_keywords": ["会議", "打ち合わせ", "議題", "結論", "長い", "決まらない", "広がり", "曖昧"],
        "topic_label": "会議運営",
        "problem_rules": [
            {
                "keywords": ["長い"],
                "problem_label": "会議時間が長くなっている",
                "business_issue": "時間効率が低下している可能性があります",
                "proposal": "議題ごとの時間配分を明確化する",
                "benefit": "会議時間の短縮と集中度の向上",
            },
            {
                "keywords": ["結論", "曖昧"],
                "problem_label": "結論や決定事項が曖昧になっている",
                "business_issue": "会議後の行動が不明確になりやすい状態です",
                "proposal": "決定事項と担当を会議内で明確化する",
                "benefit": "会議後の行動明確化と実行力の向上",
            },
            {
                "keywords": ["話", "広がり"],
                "problem_label": "議論が広がりすぎている",
                "business_issue": "本来の論点から外れやすくなっています",
                "proposal": "議題の範囲を事前共有し、進行役を明確にする",
                "benefit": "論点の集中と意思決定の迅速化",
            },
            {
                "keywords": ["決まらない"],
                "problem_label": "会議で物事が決まりにくい",
                "business_issue": "合意形成や判断が先送りされやすい状態です",
                "proposal": "会議の目的と判断事項を事前に整理する",
                "benefit": "判断スピードの向上と会議の有効性向上",
            },
        ],
        "fallback_problem": "会議運営に課題がある",
        "fallback_issue": "議論や意思決定の進め方に改善余地があります",
        "fallback_proposal": "会議の進め方やルールを見直す",
        "fallback_benefit": "会議効率の改善と意思決定の明確化",
    },
    "報告": {
        "topic_keywords": ["報告", "共有", "進捗", "粒度", "フォーマット", "バラバラ", "分かりにくい"],
        "topic_label": "報告・共有運用",
        "problem_rules": [
            {
                "keywords": ["バラバラ"],
                "problem_label": "報告の仕方にばらつきがある",
                "business_issue": "情報の比較や把握がしにくくなっています",
                "proposal": "報告フォーマットや観点を統一する",
                "benefit": "認識齟齬の削減と確認効率の向上",
            },
            {
                "keywords": ["粒度"],
                "problem_label": "報告内容の粒度が揃っていない",
                "business_issue": "必要な情報が過不足なく伝わりにくい状態です",
                "proposal": "報告項目と粒度の基準を整理する",
                "benefit": "報告品質の安定化と判断のしやすさ向上",
            },
            {
                "keywords": ["分かりにくい"],
                "problem_label": "報告内容が理解しにくい",
                "business_issue": "内容把握に追加確認が必要になりやすい状態です",
                "proposal": "結論・理由・対応方針の順で整理するルールを設ける",
                "benefit": "理解速度の向上と追加確認の削減",
            },
            {
                "keywords": ["遅い"],
                "problem_label": "報告や共有のタイミングが遅い",
                "business_issue": "課題発見や対応判断が後ろ倒しになりやすい状態です",
                "proposal": "報告タイミングや共有頻度を見直す",
                "benefit": "課題発見の早期化と対応スピード向上",
            },
        ],
        "fallback_problem": "報告・共有運用に課題がある",
        "fallback_issue": "情報共有の質やタイミングに改善余地があります",
        "fallback_proposal": "報告ルールや共有方法を見直す",
        "fallback_benefit": "情報共有の精度向上と認識合わせの効率化",
    },
}

NEGATIVE_WORDS = ["無駄", "意味ない", "最悪", "イライラ", "腹立つ", "だるい", "しんどい"]


def clean_text(text: str) -> str:
    if not text:
        return ""
    return text.strip()


def count_keyword_hits(text: str, keywords: list[str]) -> int:
    return sum(1 for kw in keywords if kw in text)


def detect_category(text: str) -> str:
    best_category = ""
    best_score = 0

    for category, rule in CATEGORY_RULES.items():
        score = count_keyword_hits(text, rule["topic_keywords"])
        if score > best_score:
            best_score = score
            best_category = category

    return best_category


def detect_problem_rule(text: str, category: str) -> dict:
    if not category:
        return {}

    rules = CATEGORY_RULES[category]["problem_rules"]
    best_rule = {}
    best_score = 0

    for rule in rules:
        score = count_keyword_hits(text, rule["keywords"])
        if score > best_score:
            best_score = score
            best_rule = rule

    return best_rule


def detect_desired_action(text: str) -> str:
    if "買い替え" in text:
        return "更新"
    if "統一" in text:
        return "統一"
    if "可視化" in text:
        return "可視化"
    if "見直し" in text:
        return "見直し"
    if "整理" in text:
        return "整理"
    return ""


def build_conclusion(category_rule: dict, desired_action: str) -> str:
    topic_label = category_rule["topic_label"]

    if desired_action == "更新":
        return f"{topic_label}について、更新を検討すべきです。"
    if desired_action == "統一":
        return f"{topic_label}について、運用の統一を検討すべきです。"
    if desired_action == "可視化":
        return f"{topic_label}について、可視化を進めるべきです。"
    if desired_action == "整理":
        return f"{topic_label}について、整理を進めるべきです。"

    return f"{topic_label}について、見直しを検討すべきです。"


def build_background(topic_label: str, problem_label: str, business_issue: str, text: str) -> str:
    return (
        f"現在、{topic_label}では「{problem_label}」状況があり、"
        f"{business_issue} "
        f"入力内容からも「{text}」という問題意識が読み取れます。"
    )


def build_proposal_text(topic_label: str, proposal: str) -> str:
    return f"{topic_label}について、{proposal}ことを提案します。"


def build_benefit_text(benefit: str) -> str:
    return f"これにより、{benefit}が期待されます。"


def build_proposal(text: str) -> str:
    cleaned = clean_text(text)
    category = detect_category(cleaned)

    if not category:
        return (
            "結論：\n現在の運用には改善の余地があります。\n\n"
            "背景・課題：\n入力内容から改善ニーズは読み取れますが、対象や問題点がやや広いため、まず改善対象を整理する必要があります。\n\n"
            "提案内容：\n対象となる業務や運用を明確にしたうえで、見直しの方向性を整理することを提案します。\n\n"
            "期待効果：\n論点の明確化により、具体的な改善検討がしやすくなります。"
        )

    category_rule = CATEGORY_RULES[category]
    problem_rule = detect_problem_rule(cleaned, category)
    desired_action = detect_desired_action(cleaned)

    if problem_rule:
        problem_label = problem_rule["problem_label"]
        business_issue = problem_rule["business_issue"]
        proposal = problem_rule["proposal"]
        benefit = problem_rule["benefit"]
    else:
        problem_label = category_rule["fallback_problem"]
        business_issue = category_rule["fallback_issue"]
        proposal = category_rule["fallback_proposal"]
        benefit = category_rule["fallback_benefit"]

    topic_label = category_rule["topic_label"]

    conclusion = build_conclusion(category_rule, desired_action)
    background = build_background(topic_label, problem_label, business_issue, cleaned)
    proposal_text = build_proposal_text(topic_label, proposal)
    benefit_text = build_benefit_text(benefit)

    return (
        f"結論：\n{conclusion}\n\n"
        f"背景・課題：\n{background}\n\n"
        f"提案内容：\n{proposal_text}\n\n"
        f"期待効果：\n{benefit_text}"
    )


def build_comments(text: str) -> list[html.Li]:
    cleaned = clean_text(text)
    category = detect_category(cleaned)

    if not category:
        return [html.Li("対象が広かったため、まず改善対象を整理する前提で構成しました。")]

    category_rule = CATEGORY_RULES[category]
    problem_rule = detect_problem_rule(cleaned, category)
    desired_action = detect_desired_action(cleaned)

    comments = [html.Li(f"入力文からカテゴリとして「{category_rule['topic_label']}」を抽出しました。")]

    if problem_rule:
        comments.append(html.Li(f"問題点として「{problem_rule['problem_label']}」を読み取りました。"))
        comments.append(html.Li(f"提案は「{problem_rule['proposal']}」の方向で組み立てました。"))
    else:
        comments.append(html.Li("個別の問題パターンに強く一致しなかったため、カテゴリ全体の見直し提案として構成しました。"))

    if desired_action:
        comments.append(html.Li(f"入力文に含まれる要望をもとに、「{desired_action}」の方向性も反映しました。"))

    if any(word in cleaned for word in NEGATIVE_WORDS):
        comments.append(html.Li("感情の強い表現は避け、上司に出しやすい中立的な表現へ変換しました。"))

    comments.append(html.Li("結論→背景・課題→提案内容→期待効果の順に整理しました。"))
    return comments


app.layout = html.Div(
    [
        html.H1("通る提案メーカー"),
        html.P("違和感・不満・愚痴をそのまま入れると、上司に通りやすい提案文に整えます。"),
        dcc.Textarea(
            id="input-text",
            placeholder="例：文書の回覧ですが、コメントほとんどなしで承認していることが頻繁していて、無駄です",
            style={"width": "100%", "height": 180, "fontSize": "18px"},
        ),
        html.Br(),
        html.Button("提案に変換する", id="convert-btn"),
        html.H2("そのまま使える提案文"),
        dcc.Textarea(
            id="output-text",
            style={"width": "100%", "height": 340, "fontSize": "18px"},
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