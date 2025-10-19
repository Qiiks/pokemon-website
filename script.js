// DOM Elements
const pokemonForm = document.querySelector("#pokemon-search-form");
const pokemonContainer = document.querySelector("#pokemon-info");
const loader = document.querySelector("#loader");
const errorMessage = document.querySelector("#error-message");

// Helper function to create DOM elements
const createElement = (tag, options = {}) => Object.assign(document.createElement(tag), options);

// Type colors map for styling type badges
const typeColors = {
  normal: "#A8A878",
  fire: "#F08030",
  water: "#6890F0",
  electric: "#F8D030",
  grass: "#78C850",
  ice: "#98D8D8",
  fighting: "#C03028",
  poison: "#A040A0",
  ground: "#E0C068",
  flying: "#A890F0",
  psychic: "#F85888",
  bug: "#A8B820",
  rock: "#B8A038",
  ghost: "#705898",
  dragon: "#7038F8",
  dark: "#705848",
  steel: "#B8B8D0",
  fairy: "#EE99AC"
};

// Type-based effects configuration
const typeEffects = {
  fire: {
    className: 'fire-effect',
    particleCount: 20,
    particleClass: 'fire-particle'
  },
  water: {
    className: 'water-effect',
    particleCount: 15,
    particleClass: 'water-drop'
  },
  grass: {
    className: 'grass-effect',
    particleCount: 12,
    particleClass: 'leaf'
  },
  electric: {
    className: 'electric-effect',
    particleCount: 10,
    particleClass: 'electric-bolt'
  },
  psychic: {
    className: 'psychic-effect',
    particleCount: 5,
    particleClass: 'psychic-ring'
  },
  ice: {
    className: 'ice-effect',
    particleCount: 20,
    particleClass: 'snowflake'
  },
  dragon: {
    className: 'dragon-effect',
    particleCount: 8,
    particleClass: 'dragon-orb'
  },
  fairy: {
    className: 'fairy-effect',
    particleCount: 15,
    particleClass: 'sparkle'
  },
  ghost: {
    className: 'ghost-effect',
    particleCount: 5,
    particleClass: 'ghost-blob'
  },
  dark: {
    className: 'dark-effect',
    particleCount: 8,
    particleClass: 'shadow'
  },
  flying: {
    className: 'flying-effect',
    particleCount: 4,
    particleClass: 'cloud'
  },
  bug: {
    className: 'bug-effect',
    particleCount: 12,
    particleClass: 'bug'
  },
  ground: {
    className: 'ground-effect',
    particleCount: 8,
    particleClass: 'rock'
  }
};

// Function to display error message
const showError = (message) => {
  errorMessage.textContent = message;
  errorMessage.style.display = "block";
  loader.style.display = "none";
};

// Function to hide error message
const hideError = () => {
  errorMessage.textContent = "";
  errorMessage.style.display = "none";
};

// Function to clear previous results
const clearResults = () => {
  pokemonContainer.innerHTML = "";
  errorMessage.style.display = "none";
  
  // Remove any active type effects
  document.querySelectorAll('.type-effect').forEach(effect => {
    effect.remove();
  });
};

// Function to show loader
const showLoader = () => {
  loader.style.display = "flex";
};

// Function to hide loader
const hideLoader = () => {
  loader.style.display = "none";
};

// Function to safely get nested data with a default value if it doesn't exist
const safeData = (data, path, defaultValue = "") => {
  if (!data) return defaultValue;
  
  const keys = path.split('.');
  let result = data;
  
  for (const key of keys) {
    if (result === undefined || result === null || !result[key]) {
      return defaultValue;
    }
    result = result[key];
  }
  
  return result !== undefined && result !== null ? result : defaultValue;
};

// Function to create type-based effects
const createTypeEffect = (types) => {
  if (!types || types.length === 0) return;
  
  // Get the primary type (first in the list)
  const primaryType = types[0].toLowerCase().trim();
  
  // Check if we have an effect for this type
  if (!typeEffects[primaryType]) return;
  
  const effectConfig = typeEffects[primaryType];
  
  // Create the effect container
  const effectContainer = createElement('div', {
    className: `type-effect ${effectConfig.className}`
  });
  
  // Create particles based on the type
  for (let i = 0; i < effectConfig.particleCount; i++) {
    const particle = createElement('div', {
      className: effectConfig.particleClass
    });
    
    // Randomize position and animation delay
    const randomX = Math.floor(Math.random() * 100);
    const randomY = Math.floor(Math.random() * 100);
    const randomDelay = Math.random() * 5;
    const randomScale = 0.5 + Math.random() * 1.5;
    
    particle.style.left = `${randomX}%`;
    particle.style.top = `${randomY}%`;
    particle.style.animationDelay = `${randomDelay}s`;
    particle.style.transform = `scale(${randomScale})`;
    particle.style.opacity = "0";
    
    // Add to container
    effectContainer.appendChild(particle);
  }
  
  // Add to body
  document.body.appendChild(effectContainer);
  
  // Activate the effect after a short delay
  setTimeout(() => {
    effectContainer.classList.add('active');
  }, 100);
  
  return effectContainer;
};

// Function to create Pokémon card (left side)
const createPokemonCard = (data) => {
  const card = createElement("div", { className: "pokemon-card" });
  
  // Pokemon name
  card.appendChild(
    createElement("h2", { 
      className: "pokemon-name",
      textContent: safeData(data, "name", "Unknown Pokémon")
    })
  );
  
  // Create image container
  const imageContainer = createElement("div", { className: "pokemon-image-container" });
  
  // Official artwork (static)
  const officialArtwork = createElement("img", {
    className: "pokemon-image official-art",
    src: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${data.id}.png`,
    alt: safeData(data, "name", "Pokémon")
  });
  
  // Animated sprite
  const animatedSprite = createElement("img", {
    className: "pokemon-image animated-sprite",
    src: `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/animated/${data.id}.gif`,
    alt: `${safeData(data, "name", "Pokémon")} animated`
  });
  
  // Add error handling for images
  officialArtwork.onerror = () => {
    officialArtwork.src = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/0.png';
  };
  
  animatedSprite.onerror = () => {
    animatedSprite.src = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/versions/generation-v/black-white/0.png';
  };
  
  // Add hover effect
  imageContainer.appendChild(officialArtwork);
  imageContainer.appendChild(animatedSprite);
  
  // Add image container to card
  card.appendChild(imageContainer);
  
  // Pokemon types
  const typeContainer = createElement("div", { className: "pokemon-types" });
  
  const typeText = safeData(data, "details.type", "Unknown");
  const types = typeText.includes("\n") ? typeText.split("\n") : [typeText];
  
  types.forEach(type => {
    if (type.trim()) {
      const typeClass = type.trim().toLowerCase();
      const typeBadge = createElement("span", {
        className: `type-badge ${typeClass}`,
        textContent: type.trim()
      });
      typeContainer.appendChild(typeBadge);
    }
  });
  
  card.appendChild(typeContainer);
  
  return card;
};

// Function to create physical details section
const createPhysicalDetails = (data) => {
  const section = createElement("div", { className: "detail-section" });
  
  section.appendChild(
    createElement("h3", {
      className: "section-title",
      textContent: "Physical Details"
    })
  );
  
  const infoList = createElement("ul", { className: "info-list" });
  
  // Height
  const heightItem = createElement("li", { className: "info-item" });
  heightItem.appendChild(createElement("span", { className: "info-label", textContent: "Height:" }));
  heightItem.appendChild(createElement("span", { 
    className: "info-value", 
    textContent: safeData(data, "details.height", "Unknown") + " m"
  }));
  infoList.appendChild(heightItem);
  
  // Weight
  const weightItem = createElement("li", { className: "info-item" });
  weightItem.appendChild(createElement("span", { className: "info-label", textContent: "Weight:" }));
  weightItem.appendChild(createElement("span", { 
    className: "info-value", 
    textContent: safeData(data, "details.weight", "Unknown") + " kg"
  }));
  infoList.appendChild(weightItem);
  
  section.appendChild(infoList);
  
  return section;
};

// Function to create abilities section
const createAbilitiesSection = (data) => {
  const abilities = safeData(data, "abilities", []);
  if (!abilities || abilities.length === 0) return null;
  
  const section = createElement("div", { className: "detail-section" });
  
  section.appendChild(
    createElement("h3", {
      className: "section-title",
      textContent: "Abilities"
    })
  );
  
  const abilitiesList = createElement("ul", { className: "info-list" });
  
  abilities.forEach(ability => {
    if (ability.trim()) {
      const abilityItem = createElement("li", { textContent: ability });
      abilitiesList.appendChild(abilityItem);
    }
  });
  
  section.appendChild(abilitiesList);
  
  return section;
};

// Function to create evolution chain section
const createEvolutionSection = (data) => {
  const evolutionChain = safeData(data, "evolution.chain", []);
  if (!evolutionChain || evolutionChain.length === 0 || evolutionChain === "N/A") return null;
  
  const section = createElement("div", { className: "detail-section" });
  
  section.appendChild(
    createElement("h3", {
      className: "section-title",
      textContent: "Evolution Chain"
    })
  );
  
  section.appendChild(
    createElement("p", {
      innerHTML: Array.isArray(evolutionChain) ? evolutionChain.join(" → ") : evolutionChain
    })
  );
  
  return section;
};

// Function to create forms section
const createFormsSection = (data) => {
  const forms = safeData(data, "evolution.forms", []);
  if (!forms || forms.length === 0 || forms === "N/A") return null;
  
  const section = createElement("div", { className: "detail-section" });
  
  section.appendChild(
    createElement("h3", {
      className: "section-title",
      textContent: "Forms"
    })
  );
  
  const formsList = createElement("ul", { className: "info-list" });
  
  if (Array.isArray(forms)) {
    forms.forEach(form => {
      if (form && form.trim()) {
        const formItem = createElement("li", { textContent: form });
        formsList.appendChild(formItem);
      }
    });
  } else {
    const formItem = createElement("li", { textContent: forms });
    formsList.appendChild(formItem);
  }
  
  section.appendChild(formsList);
  
  return section;
};

// Function to create stats section
const createStatsSection = (data) => {
  const stats = safeData(data, "stats", null);
  if (!stats) return null;
  
  const section = createElement("div", { className: "detail-section stats-container" });
  
  section.appendChild(
    createElement("h3", {
      className: "section-title",
      textContent: "Base Stats"
    })
  );
  
  const statsContainer = createElement("div");
  
  // Convert stats object to array of [name, value] pairs
  Object.entries(stats).forEach(([statName, statValue]) => {
    if (statValue !== undefined) {
      // Create stat name element
      const statNameElement = createElement("div", {
        className: "stat-name",
        textContent: statName.replace(/-/g, ' ')
      });
      
      // Create stat bar container
      const statBarContainer = createElement("div", {
        className: "stat-bar-container"
      });
      
      // Calculate width based on stat value (max 150 for visualization)
      const value = parseInt(statValue) || 0;
      const width = Math.min(value / 1.5, 100);
      
      // Create stat bar
      const statBar = createElement("div", {
        className: "stat-bar",
        style: `width: ${width}%`,
        textContent: value
      });
      
      statBarContainer.appendChild(statBar);
      
      // Add stat elements to container
      statsContainer.appendChild(statNameElement);
      statsContainer.appendChild(statBarContainer);
    }
  });
  
  section.appendChild(statsContainer);
  
  return section;
};

// Function to format move text with proper spacing
const formatMove = (move) => {
  if (Array.isArray(move)) {
    return move.join(", ");
  }
  return move;
};

// Function to create moves section
const createMovesSection = (data) => {
  const movesets = safeData(data, "movesets", []);
  if (!movesets || movesets.length === 0) return null;
  
  const section = createElement("div", { className: "detail-section moves-section" });
  
  section.appendChild(
    createElement("h3", {
      className: "section-title",
      textContent: "Movesets"
    })
  );
  
  const movesetContainer = createElement("div");
  
  // Process each moveset
  movesets.forEach((movesetData, index) => {
    if (!movesetData) return;
    
    const moveset = createElement("div", { className: "moveset" });
    
    // Add moveset name/title
    moveset.appendChild(
      createElement("h4", { 
        className: "moveset-title",
        textContent: movesetData.name || `Moveset ${index + 1}`
      })
    );
    
    // Create moves list
    const moveList = createElement("div", { className: "move-list" });
    
    // Process moves
    if (movesetData.moves && movesetData.moves.length > 0) {
      movesetData.moves.forEach((move, moveIndex) => {
        if (move) {
          const formattedMove = formatMove(move);
          const moveItem = createElement("div", { 
            className: "move-item",
            textContent: `Move ${moveIndex + 1}: ${formattedMove}`
          });
          moveList.appendChild(moveItem);
        }
      });
    }
    
    moveset.appendChild(moveList);
    movesetContainer.appendChild(moveset);
  });
  
  section.appendChild(movesetContainer);
  
  return section;
};

// Function to create type effectiveness section
const createTypeEffectivenessSection = (data) => {
  const effectiveness = safeData(data, "effectiveness", null);
  if (!effectiveness) return null;
  
  const section = createElement("div", { className: "detail-section type-effectiveness" });
  
  // Effective against
  const strongAgainst = safeData(effectiveness, "strong_against", []);
  if (strongAgainst && strongAgainst.length > 0) {
    const effectiveContainer = createElement("div");
    effectiveContainer.appendChild(
      createElement("h3", {
        className: "section-title",
        textContent: "Effective Against"
      })
    );
    
    const effectiveList = createElement("div", { className: "effectiveness-list" });
    
    strongAgainst.forEach(type => {
      if (type && type.trim()) {
        const typeClass = type.trim().toLowerCase();
        const typeChip = createElement("span", {
          className: `type-chip ${typeClass}`,
          textContent: type.trim(),
          style: `background-color: ${typeColors[typeClass] || "#777"}`
        });
        effectiveList.appendChild(typeChip);
      }
    });
    
    effectiveContainer.appendChild(effectiveList);
    section.appendChild(effectiveContainer);
  }
  
  // Weak against
  const weakAgainst = safeData(effectiveness, "weak_against", []);
  if (weakAgainst && weakAgainst.length > 0) {
    const weakContainer = createElement("div");
    weakContainer.appendChild(
      createElement("h3", {
        className: "section-title",
        textContent: "Weak Against"
      })
    );
    
    const weakList = createElement("div", { className: "effectiveness-list" });
    
    weakAgainst.forEach(type => {
      if (type && type.trim()) {
        const typeClass = type.trim().toLowerCase();
        const typeChip = createElement("span", {
          className: `type-chip ${typeClass}`,
          textContent: type.trim(),
          style: `background-color: ${typeColors[typeClass] || "#777"}`
        });
        weakList.appendChild(typeChip);
      }
    });
    
    weakContainer.appendChild(weakList);
    section.appendChild(weakContainer);
  }
  
  return section;
};

// Function to check if an object is empty
const isEmptyObject = (obj) => {
  return obj && Object.keys(obj).length === 0 && obj.constructor === Object;
};

// Initialize background layers when the page loads
document.addEventListener('DOMContentLoaded', () => {
  // Create background layers for transitions if they don't exist
  if (!document.querySelector('.bg-layer-1')) {
    const bgLayer1 = createElement('div', { className: 'bg-layer bg-layer-1' });
    const bgLayer2 = createElement('div', { className: 'bg-layer bg-layer-2' });
    
    document.body.prepend(bgLayer2);
    document.body.prepend(bgLayer1);
    
    // Set initial background
    bgLayer1.style.background = 'linear-gradient(135deg, #1a2a6c, #b21f1f, #fdbb2d)';
    bgLayer1.classList.add('animate-gradient');
  }
});

// Function to set background with crossfade
const setBackgroundWithCrossfade = (colors) => {
  // Get the background layers
  const bgLayer1 = document.querySelector('.bg-layer-1');
  const bgLayer2 = document.querySelector('.bg-layer-2');
  
  if (!bgLayer1 || !bgLayer2) return;

  // Create the new background style using extracted colors
  const [color1, color2, color3] = colors;
  const newBackground = `linear-gradient(135deg, 
    rgba(${color1[0]}, ${color1[1]}, ${color1[2]}, 0.95) 0%,
    rgba(${color2[0]}, ${color2[1]}, ${color2[2]}, 0.85) 50%,
    rgba(${color3[0]}, ${color3[1]}, ${color3[2]}, 0.95) 100%
  )`;

  // Determine which layer is currently visible
  const activeLayer = bgLayer1.style.opacity === '1' ? bgLayer1 : bgLayer2;
  const inactiveLayer = activeLayer === bgLayer1 ? bgLayer2 : bgLayer1;
  
  // Set the new background on the inactive layer
  inactiveLayer.style.background = newBackground;
  
  // Add gradient animation
  inactiveLayer.classList.add('animate-gradient');
  
  // Set initial opacity
  inactiveLayer.style.opacity = '0';
  
  // Trigger crossfade with a slight delay
  setTimeout(() => {
    requestAnimationFrame(() => {
      activeLayer.style.opacity = '0';
      inactiveLayer.style.opacity = '1';
    });
  }, 50);
};

// Function to get average color from an image region
const getColorFromRegion = (context, x, y, width, height) => {
  try {
    const imageData = context.getImageData(x, y, width, height);
    const data = imageData.data;
    let r = 0, g = 0, b = 0, count = 0;

    for (let i = 0; i < data.length; i += 4) {
      // Skip fully transparent pixels
      if (data[i + 3] === 0) continue;
      
      r += data[i];
      g += data[i + 1];
      b += data[i + 2];
      count++;
    }

    if (count === 0) return null;

    return {
      r: Math.round(r / count),
      g: Math.round(g / count),
      b: Math.round(b / count)
    };
  } catch (error) {
    console.error('Error getting color from region:', error);
    return null;
  }
};

// Function to extract dominant colors from image
const extractColors = (img) => {
  try {
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d', { willReadFrequently: true });
    
    canvas.width = img.naturalWidth || img.width;
    canvas.height = img.naturalHeight || img.height;
    
    // Draw image on canvas
    context.drawImage(img, 0, 0);
    
    // Get colors from different regions
    const topColor = getColorFromRegion(context, 0, 0, canvas.width, Math.floor(canvas.height * 0.4));
    const bottomColor = getColorFromRegion(context, 0, Math.floor(canvas.height * 0.6), canvas.width, Math.floor(canvas.height * 0.4));
    
    return { topColor, bottomColor };
  } catch (error) {
    console.error('Error extracting colors:', error);
    return { topColor: null, bottomColor: null };
  }
};

// Function to apply background gradient
const applyBackgroundGradient = (colors) => {
  if (!colors.topColor || !colors.bottomColor) {
    console.log('No valid colors extracted, using fallback');
    return;
  }
  
  const { topColor, bottomColor } = colors;
  
  // Create gradient with some transparency for better readability
  const gradient = `linear-gradient(135deg, 
    rgba(${topColor.r}, ${topColor.g}, ${topColor.b}, 0.85) 0%,
    rgba(${bottomColor.r}, ${bottomColor.g}, ${bottomColor.b}, 0.85) 100%)`;
  
  document.body.style.background = gradient;
};

// Function to display Pokémon data
const displayPokemonData = async (data) => {
  // Clear any existing error messages and loader
  hideError();
  hideLoader();
  clearResults();

  if (!data || isEmptyObject(data)) {
    showError("No data found for this Pokémon");
    return;
  }

  // Get sprite URL for color extraction
  const spriteUrl = safeData(data, "details.preview", "");

  try {
    // Create and load the image for color extraction
    const img = new Image();
    img.crossOrigin = "Anonymous";
    img.src = spriteUrl;
    
    img.onload = () => {
      // Create a new ColorThief instance
      const colorThief = new ColorThief();
      
      try {
        // Get the palette of colors (returns array of [r,g,b])
        const palette = colorThief.getPalette(img, 3);
        
        // Set the background with the extracted colors
        setBackgroundWithCrossfade(palette);
      } catch (colorError) {
        console.error('Error extracting colors:', colorError);
        // Use a neutral gradient as fallback
        setBackgroundWithCrossfade([
          [75, 75, 75],
          [50, 50, 50],
          [25, 25, 25]
        ]);
      }
    };
    
    img.onerror = () => {
      console.error('Error loading image');
      // Use a neutral gradient as fallback
      setBackgroundWithCrossfade([
        [75, 75, 75],
        [50, 50, 50],
        [25, 25, 25]
      ]);
    };
  } catch (error) {
    console.error('Error in image processing:', error);
    setBackgroundWithCrossfade([
      [75, 75, 75],
      [50, 50, 50],
      [25, 25, 25]
    ]);
  }

  // Remove any existing type attributes
  document.body.removeAttribute('data-type');
  // Remove any existing type attributes
  document.body.removeAttribute('data-type');
  document.body.removeAttribute('data-secondary-type');
  document.body.removeAttribute('data-light-type');

  // Create the Pokemon card and details
  const pokemonCard = createPokemonCard(data);
  const pokemonDetails = createElement("div", { className: "pokemon-details" });

  // Add all sections to the details
  const sections = [
    createPhysicalDetails(data),
    createAbilitiesSection(data),
    createEvolutionSection(data),
    createFormsSection(data),
    createStatsSection(data),
    createMovesSection(data),
    createTypeEffectivenessSection(data)
  ];

  // Add each section if it exists
  sections.forEach(section => {
    if (section) {
      pokemonDetails.appendChild(section);
    }
  });

  // Clear the container and add the new content
  pokemonContainer.innerHTML = '';
  pokemonContainer.appendChild(pokemonCard);
  pokemonContainer.appendChild(pokemonDetails);

  // Add animation to the sprite
  const spriteImg = document.querySelector('.pokemon-sprite');
  if (spriteImg) {
    spriteImg.classList.add('animate-sprite');
  }

  // Try to extract colors from the sprite image for the background
  try {
    if (spriteImg && spriteImg.complete) {
      // Get the palette of colors (returns array of [r,g,b])
      const palette = colorThief.getPalette(spriteImg, 3);
      
      // Set the background with the extracted colors
      setBackgroundWithCrossfade(palette);
    }
  } catch (error) {
    console.error('Error in image processing:', error);
    // Use a neutral gradient as fallback
    setBackgroundWithCrossfade([
      [75, 75, 75],
      [50, 50, 50],
      [25, 25, 25]
    ]);
  }
};

// Use configuration from config.js
const getAPIUrl = () => CONFIG.API.getBaseUrl();

// Event listener for form submission
pokemonForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  clearResults();
  showLoader();
  
  const input = new FormData(pokemonForm);
  const searchTerm = input.get("pname").trim().toLowerCase();
  
  try {
    // Use the correct API URL
    const API_URL = getAPIUrl();
    const apiEndpoint = `${API_URL}/info/${searchTerm}`;
    
    const response = await fetch(apiEndpoint);
    
    if (!response.ok) {
      throw new Error(`Failed to fetch data for ${searchTerm}`);
    }
    
    const data = await response.json();
    displayPokemonData(data);
  } catch (error) {
    console.error("Error fetching Pokémon data:", error);
    showError(`Failed to find Pokémon "${searchTerm}". Please check the spelling or try a different name.`);
  }
});