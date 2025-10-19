# PokéInfo - Comprehensive Pokémon Database

A modern web application that provides detailed information about all Pokémon using the official PokeAPI.

## 🚀 Features

- **Complete Pokémon Database**: Information on all 1302 Pokémon
- **Real-time Data**: Fetches live data from PokeAPI with intelligent caching
- **Beautiful UI**: Responsive design with Pokémon-themed animations
- **Advanced Search**: Fuzzy matching for Pokémon names
- **Type Effectiveness**: Visual representation of type strengths/weaknesses
- **Movesets**: Organized move lists grouped by category
- **Evolution Chains**: Complete evolution information
- **Stats Visualization**: Interactive stat bars with animations

## 🛠️ Tech Stack

### Backend
- **Python 3.13** - Programming language
- **FastAPI** - Modern web framework
- **SQLite** - Lightweight database with caching
- **Uvicorn** - ASGI web server

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Advanced animations, gradients, and responsive design
- **JavaScript ES6+** - Modern JavaScript with async/await
- **Fetch API** - For API communication

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)

## 🔧 Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/Qiiks/pokemon-website.git
   cd pokemon-website
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the website**
   - Backend API: http://localhost:8080
   - Frontend: Open `index.html` in your browser

## 📁 Project Structure

```
pokemon-website/
├── app.py              # FastAPI backend server
├── index.html          # Main frontend page
├── style.css           # Styling and animations
├── script.js           # Frontend JavaScript logic
├── config.js           # Configuration settings
├── pokemon.json        # Pokémon names database (1302 entries)
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
├── DEPLOYMENT.md       # Deployment instructions
└── .gitignore          # Git ignore rules
```

## 🎯 API Endpoints

### `GET /alive/`
Health check endpoint - returns "I'm alive"

### `GET /info/{name}`
Get comprehensive Pokémon information
- **Parameters**: Pokémon name or ID
- **Returns**: JSON with stats, abilities, movesets, etc.

## 💡 How It Works

1. **Data Fetching**: Uses PokeAPI as the primary data source
2. **Caching**: Implements SQLite caching to reduce API calls
3. **Fuzzy Matching**: Finds closest match for misspelled Pokémon names
4. **Background Processing**: Async data processing for optimal performance
5. **Responsive Design**: Adapts to mobile and desktop screens

## ⚙️ Configuration

The application includes a flexible configuration system (`config.js`) that:
- **Auto-detects environment** (development vs production)
- **Configurable API endpoints** for different deployment scenarios
- **UI settings** for animations and effects
- **Caching options** for performance optimization

See `DEPLOYMENT.md` for detailed configuration instructions.

## 🔮 Future Enhancements

- [ ] Add Pokémon comparison feature
- [ ] Implement team building functionality
- [ ] Add battle simulator
- [ ] Include shiny Pokémon variants
- [ ] Add generation filtering

## 📄 License

This project is for educational/portfolio purposes. Pokémon and all related properties are © of Nintendo/Game Freak.

## 👨‍💻 Author

**Sanveed Faisal** - Full Stack Developer
- GitHub: [@Qiiks](https://github.com/Qiiks)

---

*Built with ❤️ for Pokémon trainers worldwide*