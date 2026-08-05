## AI Reflection

### What are the limitations or biases in your system?
The biggest limitation is that it only knows a tiny, hand-built catalog, so it can never
recommend anything outside of it. 

### Could your AI be misused, and how would you prevent that?
On its own it's low-risk — it only suggests songs from a fixed list. The realistic misuse is
**trusting its numbers as fact**: the audio features are approximations, so someone could present
them as real Spotify data or make claims ("this song is 95% energetic") that aren't verified. 

### What surprised you while testing your AI's reliability?
How much the **grounding** mattered  

### Describe your collaboration with AI during this project.
I used Claude to code and to add the RAG feature, write tests, and explain concepts I wasn't sure about

- **Helpful suggestion:** When I ran `python3 main.py` and got a `FileNotFoundError`, the AI
  explained that I was running from the wrong folder and that the path `data/songs.csv` only
  resolves from the project root

- **Flawed / incorrect suggestion:** When I asked it to add 100+ real songs, the AI filled in
  audio-feature numbers (energy, tempo, valence, danceability, acousticness) that *looked* precise
  and official — but they were actually made-up estimates.
