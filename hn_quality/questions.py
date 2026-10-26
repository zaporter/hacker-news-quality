QUESTIONS = {
    "inferred_literacy_level": {
        "type": "score",
        "instructions": "What is the maximum literacy level of the Comment's author that can be inferred by this comment's text?",
        "criteria": [
            "5th grade. Very easy to read. Easily understood by an average 11-year-old student.",
            "6th grade. Easy to read. Conversational English for consumers.",
            "7th grade. Fairly easy to read.",
            "8th & 9th grade. Plain English. Easily understood by 13- to 15-year-old students.",
            "10th to 12th grade. Fairly difficult to read.",
            "College. Difficult to read.",
            "College graduate. Very difficult to read. Best understood by university graduates.",
            "Professional. Extremely difficult to read. Best understood by university graduates.",
        ],
    },
    "commentor_engages_with_post": {
        "type": "score",
        "instructions": "Does the comment engage with the post content in a valuable way?",
        "criteria": [
            "No. Comment is unrelated to content or only vaguely relates to the subject",
            "Partially. Comment author may have read the content but did not deeply engage",
            "Yes. Comment author clearly read and thought about the post content",
            "Expert. Comment author is related to post content as they work at a relevant company or wrote the post",
        ],
    },
    "commentor_responded_about_not_reading_content": {
        "type": "noul",
        "instructions": "Does the comment express frustration about people commenting without reading the post or insinuate that the commentor did not read the post? (or children responded that this comment was written without reading the post)",
    },
    "commentor_responded_about_hn_rules": {
        "type": "noul",
        "instructions": "Does the comment refer to a post not following hacker news rules? e.g. Title formatting or linking to the wrong source?",
    },
    # Tones can overlap (e.g. curious and snarky), so each is its own noul rather than one choice.
    "tone_snarky": {
        "type": "noul",
        "instructions": "Is the comment snarky, sarcastic, or mocking?",
    },
    "tone_kind": {
        "type": "noul",
        "instructions": "Is the comment kind or warm toward the people it addresses?",
    },
    "tone_curious": {
        "type": "noul",
        "instructions": "Does the comment show genuine curiosity, e.g. asking questions to learn more?",
    },
    "tone_dismissive": {
        "type": "noul",
        "instructions": "Is the comment dismissive of the post or of other people's ideas or work?",
    },
    "tone_helpful": {
        "type": "noul",
        "instructions": "Does the comment try to help, e.g. by answering a question, explaining, or pointing to useful resources?",
    },
    "tone_thoughtful": {
        "type": "noul",
        "instructions": "Is the comment thoughtful and substantive, showing careful reasoning?",
    },
    "tone_ideological": {
        "type": "noul",
        "instructions": "Is the comment driven by political or ideological positions rather than the specifics of the discussion?",
    },
    "comment_is_generic_tangent": {
        "type": "noul",
        "instructions": "Is the comment a generic tangent that could be posted on almost any thread about this broad subject, rather than engaging with the specifics?",
    },
    "comment_cites_evidence": {
        "type": "noul",
        "instructions": "Does the comment support its claims with evidence, such as links, data, or specific references?",
    },
    "comment_cites_personal_experience": {
        "type": "noul",
        "instructions": "Does the comment draw on the author's own first-hand experience?",
    },
    "comment_mentions_ai": {
        "type": "noul",
        "instructions": "Does the comment mention AI, LLMs, or specific AI products or models?",
    },
     "comment_mentions_programming_languages": {
        "type": "noul",
        "instructions": "Does the comment mention programming language design or specific programming languages?",
    },
}
