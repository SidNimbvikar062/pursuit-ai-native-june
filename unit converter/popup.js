document.addEventListener("DOMContentLoaded", () => {
  const unitCategorySelect = document.getElementById("unitCategorySelect");
  const valueInput = document.getElementById("valueInput");
  const fromUnitSelect = document.getElementById("fromUnit");
  const toUnitSelect = document.getElementById("toUnit");
  const swapUnitsButton = document.getElementById("swapUnitsBtn");
  const scientificNotationToggle = document.getElementById("scientificNotationToggle"); // New toggle
  const outputDisplay = document.getElementById("output");
  const errorMessage = document.getElementById("errorMessage");

  // Define all conversion factors, nested by category
  // Each category has a base unit with a factor of 1.0 (except Temperature, which uses formulas)
  // All other units are converted to/from this base unit.
  const allConversionFactors = {
    "length": {
      // Base unit: meters (m)
      "meters": { name: "Meters", factor: 1.0 },
      "kilometers": { name: "Kilometers", factor: 0.001 }, // 1 meter = 0.001 km
      "centimeters": { name: "Centimeters", factor: 100.0 }, // 1 meter = 100 cm
      "millimeters": { name: "Millimeters", factor: 1000.0 }, // 1 meter = 1000 mm
      "inches": { name: "Inches", factor: 39.3701 },   // 1 meter = 39.3701 inches
      "feet": { name: "Feet", factor: 3.28084 },      // 1 meter = 3.28084 feet
      "yards": { name: "Yards", factor: 1.09361 },    // 1 meter = 1.09361 yards
      "miles": { name: "Miles", factor: 0.000621371 }, // 1 meter = 0.000621371 miles
      "astronomical_units": { name: "Astronomical Units (AU)", factor: 1 / 149597870700 }, // 1 meter = 1/149597870700 AU
      "leagues": { name: "Leagues", factor: 1 / 4828.032 }, // 1 meter = 1/4828.032 Leagues (3 miles per league)
      "nautical_miles": { name: "Nautical Miles", factor: 1 / 1852 } // 1 meter = 1/1852 Nautical Miles
    },
    "mass": {
      // Base unit: grams (g)
      "grams": { name: "Grams", factor: 1.0 },
      "kilograms": { name: "Kilograms", factor: 0.001 }, // 1 gram = 0.001 kg
      "milligrams": { name: "Milligrams", factor: 1000.0 }, // 1 gram = 1000 mg
      "metric_tons": { name: "Metric Tons", factor: 0.000001 }, // 1 gram = 1e-6 metric tons
      "pounds": { name: "Pounds", factor: 0.00220462 }, // 1 gram = 0.00220462 pounds
      "ounces": { name: "Ounces", factor: 0.035274 }   // 1 gram = 0.035274 ounces
    },
    "speed": {
      // Base unit: meters per second (m/s)
      "meters_per_second": { name: "Meters/Second", factor: 1.0 },
      "kilometers_per_hour": { name: "Kilometers/Hour", factor: 3.6 }, // 1 m/s = 3.6 km/h
      "miles_per_hour": { name: "Miles/Hour", factor: 2.23694 },    // 1 m/s = 2.23694 mph
      "feet_per_second": { name: "Feet/Second", factor: 3.28084 },  // 1 m/s = 3.28084 ft/s
      "knots": { name: "Knots", factor: 1.94384 }                  // 1 m/s = 1.94384 knots
    },
    "acceleration": {
      // Base unit: meters per second squared (m/s²)
      "meters_per_second_squared": { name: "Meters/Second²", factor: 1.0 },
      "gravities": { name: "Gravities (g)", factor: 0.101972 }, // 1 m/s² = 0.101972 g (approx 9.80665 m/s² per g)
      "feet_per_second_squared": { name: "Feet/Second²", factor: 3.28084 } // 1 m/s² = 3.28084 ft/s²
    },
    "time": {
      // Base unit: seconds (s)
      "seconds": { name: "Seconds", factor: 1.0 },
      "milliseconds": { name: "Milliseconds", factor: 1000.0 }, // 1 second = 1000 ms
      "minutes": { name: "Minutes", factor: 1/60 },             // 1 second = 1/60 minutes
      "hours": { name: "Hours", factor: 1/3600 },               // 1 second = 1/3600 hours
      "days": { name: "Days", factor: 1/86400 },                // 1 second = 1/86400 days
      "weeks": { name: "Weeks", factor: 1/(86400 * 7) },       // 1 second = 1/(86400 * 7) weeks
      "years": { name: "Years", factor: 1/31536000 }            // 1 second = 1/31536000 years (approx 365 days)
    },
    "volume": {
      // Base unit: liters (L)
      "liters": { name: "Liters", factor: 1.0 },
      "milliliters": { name: "Milliliters", factor: 1000.0 }, // 1 liter = 1000 mL
      "cubic_meters": { name: "Cubic Meters", factor: 0.001 }, // 1 liter = 0.001 cubic meters
      "cubic_centimeters": { name: "Cubic Centimeters", factor: 1000.0 }, // 1 liter = 1000 cm³
      "cubic_inches": { name: "Cubic Inches", factor: 61.0237 }, // 1 liter = 61.0237 in³
      "gallons_us_liquid": { name: "Gallons (US Liquid)", factor: 0.264172 }, // 1 liter = 0.264172 US liquid gallons
      "quarts_us_liquid": { name: "Quarts (US Liquid)", factor: 1.05669 },   // 1 liter = 1.05669 US liquid quarts
      "cubic_feet": { name: "Cubic Feet", factor: 0.0353147 } // 1 liter = 0.0353147 ft³
    },
    "area": {
      // Base unit: square meters (m²)
      "square_meters": { name: "Square Meters", factor: 1.0 },
      "square_kilometers": { name: "Square Kilometers", factor: 0.000001 }, // 1 m² = 1e-6 km²
      "square_centimeters": { name: "Square Centimeters", factor: 10000.0 }, // 1 m² = 10000 cm²
      "square_millimeters": { name: "Square Millimeters", factor: 1000000.0 }, // 1 m² = 1e6 mm²
      "acres": { name: "Acres", factor: 0.000247105 }, // 1 m² = 0.000247105 acres
      "hectares": { name: "Hectares", factor: 0.0001 }, // 1 m² = 0.0001 hectares
      "square_feet": { name: "Square Feet", factor: 10.7639 }, // 1 m² = 10.7639 ft²
      "square_miles": { name: "Square Miles", factor: 0.000000386102 }, // 1 m² = 3.86102e-7 mi²
      "square_yards": { name: "Square Yards", factor: 1.19599 } // 1 m² = 1.19599 yd²
    },
    "pressure": {
      // Base unit: Pascals (Pa)
      "pascals": { name: "Pascals", factor: 1.0 },
      "kilopascals": { name: "Kilopascals", factor: 0.001 }, // 1 Pa = 0.001 kPa
      "pounds_per_square_inch": { name: "Pounds per Square Inch (psi)", factor: 0.000145038 }, // 1 Pa = 0.000145038 psi
      "atmospheres": { name: "Atmospheres (atm)", factor: 0.00000986923 }, // 1 Pa = 9.86923e-6 atm
      "bar": { name: "Bar", factor: 0.00001 } // 1 Pa = 1e-5 bar
    },
    "temperature": {
      // Temperature uses specific conversion formulas, not just factors relative to a base.
      // The 'factor' here is just a placeholder and not used for linear conversion.
      "celsius": { name: "Celsius", factor: 1.0 },
      "fahrenheit": { name: "Fahrenheit", factor: 1.0 },
      "kelvin": { name: "Kelvin", factor: 1.0 }
    }
  };

  /**
   * Populates the 'From Unit' and 'To Unit' dropdowns based on the selected category.
   * @param {string} category The selected unit category (e.g., "length", "mass").
   */
  function populateUnitsDropdowns(category) {
    fromUnitSelect.innerHTML = ''; // Clear existing options
    toUnitSelect.innerHTML = '';    // Clear existing options

    const units = allConversionFactors[category];
    if (!units) {
      console.error(`JS: No units defined for category: ${category}`);
      return;
    }

    for (const unitKey in units) {
      if (units.hasOwnProperty(unitKey)) {
        const optionFrom = document.createElement('option');
        optionFrom.value = unitKey;
        optionFrom.textContent = units[unitKey].name;
        fromUnitSelect.appendChild(optionFrom);

        const optionTo = document.createElement('option');
        optionTo.value = unitKey;
        optionTo.textContent = units[unitKey].name;
        toUnitSelect.appendChild(optionTo);
      }
    }
    // Set default selections after populating
    fromUnitSelect.value = Object.keys(units)[0]; // Select first unit by default
    toUnitSelect.value = Object.keys(units)[0];   // Select first unit by default
  }

  /**
   * Converts temperature between Celsius, Fahrenheit, and Kelvin.
   * @param {number} value The numerical temperature value.
   * @param {string} fromUnit The unit to convert from ("celsius", "fahrenheit", "kelvin").
   * @param {string} toUnit The unit to convert to ("celsius", "fahrenheit", "kelvin").
   * @returns {number|null} The converted temperature, or null if units are invalid.
   */
  function convertTemperature(value, fromUnit, toUnit) {
    let tempInCelsius;

    // Convert from source unit to Celsius first
    if (fromUnit === "celsius") {
      tempInCelsius = value;
    } else if (fromUnit === "fahrenheit") {
      tempInCelsius = (value - 32) * 5 / 9;
    } else if (fromUnit === "kelvin") {
      tempInCelsius = value - 273.15;
    } else {
      console.error("JS: Invalid 'from' temperature unit.");
      return null;
    }

    // Convert from Celsius to target unit
    if (toUnit === "celsius") {
      return tempInCelsius;
    } else if (toUnit === "fahrenheit") {
      return (tempInCelsius * 9 / 5) + 32;
    } else if (toUnit === "kelvin") {
      return tempInCelsius + 273.15;
    } else {
      console.error("JS: Invalid 'to' temperature unit.");
      return null;
    }
  }

  /**
   * Converts a numerical value between units of a given category.
   * Dispatches to convertTemperature for temperature conversions.
   * @param {number} value The numerical value to convert.
   * @param {string} category The category of units (e.g., "length", "mass").
   * @param {string} fromUnit The unit to convert from.
   * @param {string} toUnit The unit to convert to.
   * @returns {number|null} The converted value, or null if units or category are invalid.
   */
  function convertUnits(value, category, fromUnit, toUnit) {
    console.log(`JS: Converting value=${value}, category=${category}, fromUnit=${fromUnit}, toUnit=${toUnit}`);

    if (category === "temperature") {
      return convertTemperature(value, fromUnit, toUnit);
    }

    const unitsInSelectedCategory = allConversionFactors[category];

    if (!unitsInSelectedCategory || !(fromUnit in unitsInSelectedCategory) || !(toUnit in unitsInSelectedCategory)) {
      console.error("JS: Invalid category or units selected.");
      return null;
    }

    try {
      // Convert the value to the base unit of the selected category
      const valueInBaseUnit = value / unitsInSelectedCategory[fromUnit].factor;
      console.log(`JS: Value in base unit (${category}): ${valueInBaseUnit}`);

      // Convert from the base unit to the target unit
      const convertedValue = valueInBaseUnit * unitsInSelectedCategory[toUnit].factor;
      console.log(`JS: Converted value: ${convertedValue}`);
      return convertedValue;
    } catch (e) {
      console.error("JS: Error during conversion:", e);
      return null;
    }
  }

  /**
   * Performs the conversion and updates the display.
   */
  function performConversion() {
    errorMessage.textContent = ""; // Clear previous error messages

    const value = parseFloat(valueInput.value);
    const category = unitCategorySelect.value;
    const fromUnit = fromUnitSelect.value;
    const toUnit = toUnitSelect.value;
    const useScientificNotation = scientificNotationToggle.checked; // Get toggle state

    // Basic validation
    if (isNaN(value)) {
      errorMessage.textContent = "Please enter a valid number.";
      outputDisplay.textContent = "0";
      return;
    }

    if (!fromUnit || !toUnit || !category) {
      errorMessage.textContent = "Please select a category, 'From' unit, and 'To' unit.";
      outputDisplay.textContent = "0";
      return;
    }

    const result = convertUnits(value, category, fromUnit, toUnit);

    if (result !== null) {
      let formattedResult;

      if (useScientificNotation) {
        // If toggle is ON, always use scientific notation (unless result is exactly 0)
        formattedResult = result === 0 ? "0" : result.toExponential(4);
      } else {
        // If toggle is OFF, use traditional formatting, but fallback to scientific for extreme numbers
        if (Math.abs(result) >= 1e9 || (Math.abs(result) > 0 && Math.abs(result) < 1e-6)) {
          formattedResult = result.toExponential(4); // Scientific notation for very large/small
        } else {
          // Use toLocaleString for comma separation and controlled decimal places
          formattedResult = result.toLocaleString('en-US', {
            minimumFractionDigits: 0,
            maximumFractionDigits: 4,
            useGrouping: true
          });
        }
      }
      outputDisplay.textContent = formattedResult;
    } else {
      errorMessage.textContent = "Conversion failed. Please check your inputs and units.";
      outputDisplay.textContent = "0";
    }
  }

  // --- Event Listeners ---

  // Initial population of unit dropdowns when the page loads
  const initialCategory = unitCategorySelect.value;
  populateUnitsDropdowns(initialCategory);
  performConversion(); // Perform initial conversion on load

  // Event listener for category change
  unitCategorySelect.addEventListener("change", (event) => {
    const selectedCategory = event.target.value;
    populateUnitsDropdowns(selectedCategory);
    performConversion(); // Perform conversion after category changes and units are re-populated
  });

  // Event listener for input value changes (for real-time conversion)
  valueInput.addEventListener("input", performConversion);

  // Event listeners for unit dropdown changes (for real-time conversion)
  fromUnitSelect.addEventListener("change", performConversion);
  toUnitSelect.addEventListener("change", performConversion);

  // Event listener for Scientific Notation toggle change
  scientificNotationToggle.addEventListener("change", performConversion);

  // Event listener for Swap button click
  swapUnitsButton.addEventListener("click", () => {
    const currentFromUnit = fromUnitSelect.value;
    const currentToUnit = toUnitSelect.value;

    fromUnitSelect.value = currentToUnit;
    toUnitSelect.value = currentFromUnit;

    // After swapping, trigger a conversion
    performConversion();
  });
});
