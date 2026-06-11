# 1. Dataset Overview (Kaggle Dataset)

This application is powered by a recent Netflix dataset retrieved from **Kaggle** (`netflix_movies_detailed_up_to_2025.csv` and its TV show counterpart).

* **Data Content**: It contains metadata for both Netflix Movies and TV Shows.
* **Key Features**: Beyond basic information (title, genre, director, cast, release date), it includes advanced financial and engagement metrics such as **budget, revenue, viewer ratings, and global popularity**.
* **Significance**: By linking creative metadata with financial outcomes, this dataset allows for a deep, quantitative analysis of OTT content performance rather than a simple listing of titles.

---

# 2. Code Architecture (Internal Logic)

The backend logic is built using a clean **[Data Preprocessing ➔ Global Filtering ➔ Modular Visualization]** pipeline.

* **Memory Optimization (`@st.cache_data`)**: The app utilizes Streamlit’s caching mechanism to load the heavy Kaggle datasets into memory once. This prevents redundant file I/O operations and ensures fast loading times during user interactions.
* **Data Integration & Metric Engineering**: The script merges the separate movie and TV show dataframes into a unified structure. It programmatically derives critical business metrics: **Profit** (Revenue - Budget) and **Return on Investment (ROI)** (Profit / Budget * 100).
* **Dynamic Interactive System**: When a user changes the sidebar filters, the entire application dynamically slices the master dataframe (`filtered_df`), updating all charts and tables across the dashboard in real-time.

---

# 3. Streamlit App Features (User Interface)

The dashboard organizes complex insights into **four distinct, interactive tabs**, each focusing on a specific business dimension.

* **Tab 1. Financial & ROI Analysis**
  * Maps out budget and revenue data from Kaggle to display the **Top 10 Highest-Grossing Blockbusters**.
  * Evaluates the **Top 10 Most Cost-Effective Genres** based on average ROI, helping users identify high-yield, low-budget content categories.
* **Tab 2. Hitmaker (Director & Cast)**
  * Aggregates historical performance data to ranks the **Top 10 Most Influential Directors** on the platform by average popularity and rating.
  * Features a **Live Actor Search Bar** that lets users input an artist's name to instantly filter and review their specific career performance metrics on Netflix.
* **Tab 3. Seasonality Trends**
  * Displays a grouped bar chart of content release counts by month. This visually proves Netflix's **strategic distribution calendar**, showing how the platform scales up content supply during peak seasons or holidays.
* **Tab 4. Content Strategy Simulator**
  * Serves as a data-driven decision tool for producers and executives. Users can adjust inputs for a hypothetical project, including genre, target language, and estimated budget.
  * The app looks up historical patterns of matching titles to instantly output key performance indicators (KPIs): **[Expected Viewer Rating], [Expected Global Popularity], and [Expected Box Office Revenue]**.
