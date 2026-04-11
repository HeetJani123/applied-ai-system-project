# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Avoid code here. Pretend you are explaining the idea to a friend who does not program.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

One weakness I found is that the recommender can still over-favor songs that match energy very closely, even when mood is only a partial fit. That means a high-energy song can rise near the top for a user who does not really want that emotional tone. The dataset is also small, so a few repeated genres like pop and lofi have a bigger influence than they would in a real music catalog. Because the score mostly depends on genre, mood, and energy, it ignores lyrics, artist variety, and context like whether someone wants music for studying versus exercising. That creates a simple but noticeable filter bubble around the most common styles in the starter data.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested four profiles: High-Energy Pop, Chill Lofi, Deep Intense Rock, and a conflicting profile with high energy but a sad mood. The strongest results usually matched my intuition: the pop profile preferred "Sunrise City," the lofi profile preferred "Library Rain," and the intense rock profile preferred "Storm Runner." What surprised me was that the conflicting profile still pushed very energetic songs to the top, even when the mood did not match well. That showed me the energy score can dominate the ranking when the target energy is high. I also noticed that the same songs can stay near the top across multiple profiles if they are close to the user's energy target, which makes sense mathematically but can reduce variety.

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  
