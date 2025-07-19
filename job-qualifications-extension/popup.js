document.getElementById("submitBtn").addEventListener("click", async () => {
  const jobDescription = document.getElementById("jobDescription").value;
  const output = document.getElementById("output");

  // Basic validation for empty input
  if (!jobDescription.trim()) {
    output.innerHTML = '<p class="text-red-500">Please paste a job description to analyze.</p>';
    return;
  }

  output.innerHTML = '<p class="text-blue-500">Extracting qualifications... Please wait.</p>'; // Loading indicator

  const apiKey = "AIzaSyBSX7Yhj4kTKuIOxw-lEhIGzltp0hb5hPA"; // <--- PASTE YOUR API KEY HERE

  const prompt = `Extract only the required qualifications from the following job description. List them clearly, preferably as bullet points. If there are no explicit "required qualifications," state that. Avoid including responsibilities, preferred qualifications, or company benefits.

Job Description:
${jobDescription}`;

  // Gemini API payload
  const payload = {
    contents: [{
      parts: [{ text: prompt }]
    }],
    generationConfig: {
      // You can adjust temperature, topK, topP if needed for different response styles
      // For qualification extraction, a lower temperature might be better for precision.
      temperature: 0.2,
      maxOutputTokens: 500 // Limit the response length to avoid overly long outputs
    }
  };

  try {
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${apiKey}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (response.ok) {
      const data = await response.json();
      // Check if candidates and content parts exist in the response
      if (data.candidates && data.candidates.length > 0 &&
          data.candidates[0].content && data.candidates[0].content.parts &&
          data.candidates[0].content.parts.length > 0) {
        const extractedText = data.candidates[0].content.parts[0].text;
        output.textContent = extractedText;
      } else {
        output.innerHTML = '<p class="text-red-500">Error: No valid response from Gemini API. Check API key or input.</p>';
        console.error("Gemini API response structure unexpected:", data);
      }
    } else {
      // Handle HTTP errors (e.g., 400, 401, 403, 500)
      const errorData = await response.json();
      output.innerHTML = `<p class="text-red-500">Error: API request failed (Status: ${response.status}).</p>`;
      console.error("API Error:", errorData);
    }
  } catch (error) {
    // Handle network errors or other exceptions
    output.innerHTML = '<p class="text-red-500">Error: Could not connect to the Gemini API. Check your internet connection or console for details.</p>';
    console.error("Fetch error:", error);
  }
});