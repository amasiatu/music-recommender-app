# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- Some features that each `Song` will use int the system will be genre, mood, energy, and acousticness mainly weighted by the order in the list due to experiencing those things mattering more and not allowing the system to mix up scoring with so many options of features
- `UserProfile` stores the users location, favorite genre, favorite mood, target energy, and a short range for acoustic tendencies
- My `Recommender` computes a score for each song by out of 100 scoring and weighing genre highest followed after mood, taregt energy and acoustic tendency
- Using ranking we find the number and compare it to the users last song or their listen history

- Data flow plan: Input(User prefs) -> Load Songs(Data) -> Score Songs(Scoring Logic) -> Songs Score judged(recommender) -> Output (top k highest songs recommended)
  - Some potential biases may be on certain genres being associated with certain energy levels or the data having more songs of a certain genre and less of another

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

User profile:
  genre: pop
  mood: happy
  energy: 0.8

Top recommendations:

Sunrise City - Score: 1.00
Because: matches your favorite genre (pop), matches your mood (happy), energy is close to your target (0.82 vs 0.80)

Gym Hero - Score: 0.72
Because: matches your favorite genre (pop), energy is close to your target (0.93 vs 0.80)

Rooftop Lights - Score: 0.49
Because: matches your mood (happy), energy is close to your target (0.76 vs 0.80)

Night Drive Loop - Score: 0.24
Because: energy is close to your target (0.75 vs 0.80)

Concrete Sunrise - Score: 0.23
Because: energy is close to your target (0.72 vs 0.80)

{User profile:
  genre: rock
  mood: sad
  energy: 0.7

Top recommendations:

Storm Runner - Score: 0.70
Because: matches your favorite genre (rock)

Concrete Sunrise - Score: 0.24
Because: energy is close to your target (0.72 vs 0.70)

Night Drive Loop - Score: 0.24
Because: energy is close to your target (0.75 vs 0.70)

Rooftop Lights - Score: 0.23
Because: energy is close to your target (0.76 vs 0.70)

Backroad Dust - Score: 0.23
Because: energy is close to your target (0.60 vs 0.70)}

{User profile:
  genre: rap
  mood: sad
  energy: 0.4

Top recommendations:

Focus Flow - Score: 0.25
Because: energy is close to your target (0.40 vs 0.40)

Midnight Coding - Score: 0.24
Because: energy is close to your target (0.42 vs 0.40)

Dust and Pinewood - Score: 0.24
Because: energy is close to your target (0.38 vs 0.40)

Coffee Shop Stories - Score: 0.24
Because: energy is close to your target (0.37 vs 0.40)

Library Rain - Score: 0.24
Because: energy is close to your target (0.35 vs 0.40)}

{ User profile:
  genre: hip-hop
  mood: sad
  energy: 0.6

Top recommendations:

Backroad Dust - Score: 0.25
Because: energy is close to your target (0.60 vs 0.60)

Island Time - Score: 0.24
Because: energy is close to your target (0.55 vs 0.60)

Concrete Sunrise - Score: 0.22
Because: energy is close to your target (0.72 vs 0.60)

Velvet Hours - Score: 0.22
Because: energy is close to your target (0.48 vs 0.60)

Night Drive Loop - Score: 0.21
Because: energy is close to your target (0.75 vs 0.60)
}

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



