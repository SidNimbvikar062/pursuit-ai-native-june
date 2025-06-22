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