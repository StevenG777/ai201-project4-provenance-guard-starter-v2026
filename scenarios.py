"""
What your test runs. <- UNIT 8, MILESTONE 3

Criteria (see criteria.md):
  1. False positives   - 10 pieces I wrote myself; at most 2 labelled "ai".
  2. Score spread      - 10 clearly-AI and 10 clearly-human pieces; every AI
                         confidence above every human confidence.
  3. Label coverage    - the same 20 inputs; each of the three labels >= 5 times.
  4. Appeal path       - NOT here. run_eval.py only sends /submit, so criterion 4
                         is run by run_appeal_check.py (3 trials, real output).
  5. Bad input         - missing, empty and whitespace-only text each return 400.

Human pieces 1-3 are single sentences I wrote. Pieces 4-10 are the sentences of
one essay I wrote at school, cut into seven
chunks at sentence boundaries. They are not independent samples (one writer, one
essay), which limits what criterion 1 can show. Spelling and grammar are exactly
as written.
"""

HUMAN = [
    "Today is a very good day and I am happy",
    "Despite work it not busy, I still feel like my energy was drained by customer, plus I caught cold from being showered by the rain outside, I feel really sleepy",
    "If gradient descent is part of math optimization, dynamic programming should deserve its own branch in the same field.",
    "In this picture i see three little girls with blond hair and wear the dirty clothes,they are standing  in the doorway of the house. The house is made of wood and the doorway is made of wood too.",
    "The wood is not painted and it does not look finished.The girls appear to be three years old and four years old and five years old. Both wear no shoes,except their mother.",
    "Both girls are barefoot and their feets are very dirty. They are not smiling.",
    "I can infer that the girls are very very poor and they are seem unhappy to live in this world .  This picture is from the Great depression,1930s, i think they may be don\u2019t go to school.",
    "They maybe don\u2019t have enough to eat.They may be don\u2019t have a clothes is nice.I worry about that the kids may be have not a good future, but i think so they are don\u2019t worrying about for their future whether a good future or bad future because of they are poor.",
    "This picture makes me feel sad.I feel sad for the three girls and their mother in the picture because i think they are living during the Great Depression, they have a  hard  life, and they are have no job, and lose their money, and then someone even lose their house because of the stock market crash,this is the main cause of the Great Depression.",
    "However, i still want to talk to them,if the fact is cruel, don\u2019t give up your life,because your life is very precious.,i thinks that you can do your best work for your life. I think this picture is very good is the representative picture what life was like during the Great Depression.It shows tremendous poor which is what many people experience during the Great Depression,1929s-1932s.",
]

# Written by Claude (an AI) for this test, in the usual assistant style.
AI = [
    "Effective time management is a cornerstone of professional success. By prioritizing tasks, setting clear goals, and minimizing distractions, individuals can significantly enhance their productivity. Moreover, regular reflection on one's habits allows for continuous improvement over time.",
    "Climate change represents one of the most pressing challenges facing humanity today. Rising global temperatures contribute to more frequent extreme weather events, sea level rise, and disruptions to ecosystems. Addressing this issue requires coordinated action from governments, businesses, and individuals alike.",
    "Regular physical exercise offers numerous benefits for both body and mind. It strengthens the cardiovascular system, improves mood, and helps maintain a healthy weight. Furthermore, consistent activity has been shown to reduce the risk of chronic diseases.",
    "Artificial intelligence is transforming the way organizations operate across industries. From automating routine tasks to providing deeper insights from data, these technologies offer significant opportunities. However, it is important to consider the ethical implications of their deployment.",
    "A balanced diet plays a vital role in maintaining overall health and well-being. It should include a variety of fruits, vegetables, whole grains, and lean proteins. By making mindful food choices, individuals can support their energy levels and long-term health.",
    "Effective communication is essential for building strong relationships in both personal and professional settings. Active listening, clarity, and empathy are key components of meaningful dialogue. When these elements are present, misunderstandings are reduced and collaboration flourishes.",
    "The rapid growth of e-commerce has reshaped the retail landscape in recent years. Consumers now enjoy greater convenience, a wider selection of products, and competitive pricing. As a result, traditional businesses must adapt to remain relevant in an increasingly digital marketplace.",
    "Education serves as a powerful catalyst for personal and societal development. It equips individuals with the knowledge and skills necessary to navigate an increasingly complex world. Investing in quality education ultimately benefits communities and economies as a whole.",
    "Cybersecurity has become a critical concern for individuals and organizations alike. Strong passwords, regular software updates, and employee training can significantly reduce the risk of breaches. Ultimately, a proactive approach to security is far more effective than a reactive one.",
    "Travel provides valuable opportunities to experience new cultures and broaden one's perspective. Whether exploring a bustling city or a quiet countryside, each destination offers unique insights. Through these experiences, travelers develop greater empathy and a deeper appreciation for the world.",
]

SCENARIOS = [
    {"name": "my own writing", "criterion": 1, "texts": HUMAN},
    # AI first, then human: the first 10 results are AI, the last 10 are human.
    {"name": "score spread", "criterion": 2, "texts": AI + HUMAN},
    {"name": "label coverage", "criterion": 3, "texts": AI + HUMAN},
    # Criterion 4 (appeal path) is run by run_appeal_check.py, not here.
    {
        "name": "bad input",
        "criterion": 5,
        "bodies": [
            {"creator_id": "eval_bad_missing"},                      # no text field
            {"text": "", "creator_id": "eval_bad_empty"},            # empty string
            {"text": "   \n\t  \n ", "creator_id": "eval_bad_blank"},  # whitespace only
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
