Universal Unit Converter Browser Extension
A comprehensive and intuitive browser extension for converting between various units of measurement, designed for quick and easy use directly from your browser's toolbar.

About This Project
This project delivers a versatile Unit Converter as a browser extension. It allows users to convert values across multiple categories, including:

Length (including niche units like Astronomical Units, Leagues, Nautical Miles)

Mass

Speed/Velocity

Acceleration

Time

Volume

Area

Pressure

Temperature

Key features include:

Real-time Conversion: Results update instantly as you type or change units.

Unit Swapping: A dedicated button to quickly swap "From" and "To" units.

Readability Features: Automatically adds comma separators for large numbers and offers a toggle for scientific notation for extremely large or small results.

User-Friendly UI: Features a dark mode for better visibility in low-light conditions.

How It Works
The Universal Unit Converter is a client-side browser extension primarily built with HTML, CSS (Tailwind CSS), and JavaScript.

Data Structure (The Core): All unit conversion factors and unit names are meticulously stored in a central JavaScript allConversionFactors object. This object is structured like a "dictionary of dictionaries" (or a hashmap), enabling highly efficient, constant-time (O(1)) lookups for any given category and unit. This optimized data access is crucial for the real-time conversion experience.

Real-time Conversion Logic:

Unlike traditional converters that require a "Convert" button, this extension automatically performs conversions.

Event listeners are attached to the input value field, the "From Unit" dropdown, and the "To Unit" dropdown. Any change in these inputs triggers the performConversion() function.

The "Swap Units" button also triggers a re-conversion after exchanging the selected units.

Conversion Mechanism:

For most unit categories (length, mass, speed, etc.), conversions are handled by first converting the input value to a predefined base unit (e.g., meters for length, grams for mass) and then converting from that base unit to the target unit. This simplifies the conversion logic significantly.

Temperature Conversions: Temperature conversions (Celsius, Fahrenheit, Kelvin) are treated as a special case due to their non-linear formulas. A dedicated convertTemperature() function handles these specific calculations.

Output Formatting:

The performConversion() function intelligently formats the output for readability.

It uses Number.prototype.toLocaleString() to add comma separators (e.g., 1,000,000) for standard large numbers.

For extremely large ( ≥10 
9
  ) or very small ( <10 
−6
 , non-zero) numbers, it automatically switches to Number.prototype.toExponential() for scientific notation (e.g., 1.2345e+9).

A user-toggleable switch allows the user to explicitly force scientific notation on or off, overriding the automatic behavior.

User Interface:

The UI is styled using Tailwind CSS for a clean, responsive design.

A dark mode color scheme (black background, white text) is implemented for enhanced visibility.

The layout is carefully managed with box-sizing: border-box; and explicit width/padding/margin properties to ensure elements fit correctly within the compact browser extension window without requiring a scrollbar.

How to Run It
This project is designed to be loaded as an unpacked browser extension (e.g., in Google Chrome).

Download the Project Files:

Ensure you have all the necessary files: manifest.json, popup.html, popup.js, style.css, and your icon image (6424.jpg).

Open Chrome Extensions Page:

Open your Google Chrome browser.

Type chrome://extensions/ in the address bar and press Enter.

Enable Developer Mode:

In the top-right corner of the Extensions page, toggle on "Developer mode".

Load the Extension:

Click on the "Load unpacked" button that appears.

A file dialog will open. Navigate to the directory where you saved your project files (the folder containing manifest.json).

Select that folder and click "Select Folder" (or similar, depending on your OS).

Pin the Extension (Optional, but Recommended):

After loading, you should see your "Universal Unit Converter" extension appear in the list.

To easily access it, click the puzzle piece icon (Extensions icon) in your Chrome toolbar.

Find "Universal Unit Converter" in the dropdown and click the pin icon next to it. This will make its icon (6424.jpg) visible directly in your toolbar.

Use the Converter:

Click the extension icon in your toolbar to open the popup.

Enter a value, select your "From" and "To" units, choose a category, and toggle scientific notation as desired. The conversion will happen automatically!