document.addEventListener("DOMContentLoaded", () => {
    const valueInput = document.getElementById("valueInput");
    const fromUnitSelect = document.getElementById("fromUnit");
    const toUnitSelect = document.getElementById("toUnit");
    const convertButton = document.getElementById("convertBtn"); // Changed from submitBtn
    const outputDisplay = document.getElementById("output"); // Changed from output
    const errorMessage = document.getElementById("errorMessage");
  
    // Conversion factors relative to meters
    // 1 meter = X unit (e.g., 1 meter = 1.0 meters, 1 meter = 0.001 kilometers)
    const conversionFactors = {
      "meters": 1.0,
      "kilometers": 0.001,
      "centimeters": 100.0,
      "inches": 39.3701,
      "feet": 3.28084,
      "miles": 0.000621371
    };
  
    /**
     * Converts a numerical value from one length unit to another.
     * @param {number} value The numerical value to convert.
     * @param {string} fromUnit The unit to convert from (e.g., "meters", "feet").
     * @param {string} toUnit The unit to convert to (e.g., "kilometers", "inches").
     * @returns {number|null} The converted value, or null if units are invalid.
     */
    function convertLength(value, fromUnit, toUnit) {
      console.log(`JS: Converting value=${value}, fromUnit=${fromUnit}, toUnit=${toUnit}`);
  
      if (!(fromUnit in conversionFactors) || !(toUnit in conversionFactors)) {
        console.error("JS: Invalid unit selected.");
        return null;
      }
  
      try {
        // Convert the value to a base unit (meters) first
        const valueInMeters = value / conversionFactors[fromUnit];
        console.log(`JS: Value in meters: ${valueInMeters}`);
  
        // Convert from meters to the target unit
        const convertedValue = valueInMeters * conversionFactors[toUnit];
        console.log(`JS: Converted value: ${convertedValue}`);
        return convertedValue;
      } catch (e) {
        console.error("JS: Error during conversion:", e);
        return null;
      }
    }
  
    convertButton.addEventListener("click", () => {
      errorMessage.textContent = ""; // Clear previous error messages
  
      const value = parseFloat(valueInput.value);
      const fromUnit = fromUnitSelect.value;
      const toUnit = toUnitSelect.value;
  
      // Basic validation
      if (isNaN(value)) {
        errorMessage.textContent = "Please enter a valid number.";
        outputDisplay.textContent = "0";
        return;
      }
  
      if (!fromUnit || !toUnit) {
        errorMessage.textContent = "Please select both 'From' and 'To' units.";
        outputDisplay.textContent = "0";
        return;
      }
  
      const result = convertLength(value, fromUnit, toUnit);
  
      if (result !== null) {
        outputDisplay.textContent = result.toFixed(4); // Display with 4 decimal places
      } else {
        errorMessage.textContent = "Conversion failed. Please check units.";
        outputDisplay.textContent = "0";
      }
    });
  });
  