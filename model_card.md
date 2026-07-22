# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeCheck**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- According to the data, the kind of recs that the recommender chooses it will be based on banker
- It assumed they have dexterity to more their fingers have after 
- This is for classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- Genre, energy , mood are the main factors in the scoring logc  
- The main ones that are considered are genre and energy
- The model adds weight to each song
- So we changed the logic of scoring people  

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- 18
- the main genre represented is pop
- No i didnt add or remove data  
- yeah there is a taste missing 

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- It gives reasonable results  
- yeah its unbalanced because some of the energy levels are mpt prsent 
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- The user's mood is pretty much not represented in the recommendation, so a happy and sad listener get the same recs 
- Genres are unrelated islands some music genres are similar to each other like hip hop and rap because genres are scored by exact match  
- The energy gap still accounts for extreme energy and not moderate ones because the data is quite skewed   

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- I tested user prefrences from the initial part in step 2 then I added 3 more that had different genres with seemingly contradictory energy levels  
- What I looked for in the recommendation is that if they couldn't find the a song that matched the genre that they would find a similar genre to match it with along with a similar energy level  
- What surprised me about this project and how much data I need to make accurate observations  
- I didn't really run any tests in particular   

For comparison of the user profile2 with genre rap and the user profile3 with the genre hip hop. and profile2 prefers lower energy songs over and profile3 likes songs with a bit more high energy. So im not surprised that the results of profile3 is a bit higher

For comparison of the user profile which is rock genre and profile 1 which is pop genre and it seems as though pop was socred by energy and rock scored by genre 

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Use more than 3 variables to create recs  
- The explanation doesnt include everything   
- The model doesnt reward diversity  
- User genres are isolated so no connection between any of them and I would want to improve on that  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- I learned that recommender systems take a lot of calculations and complexities to increase  
- Something interesting was that the genres weren't related  
- This changed the way I think about apps because it shows me that my recs has a lot going on in the background even though its simple for me  
