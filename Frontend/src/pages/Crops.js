import React, { useState } from React;

function Crops() {
  const [query, setQuery] = useState("Which paddy variety suits unpredictable weather?");
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);

  const askCrops = async () => {
    setLoading(true);
    try {
      const res = await fetch("http://localhost:8000/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();
      setAnswer(data.answer);
    } catch (err) {
      setAnswer("⚠️ Failed to fetch crop advisory. Please try again.");
    }
    setLoading(false);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Crop Advisory</h1>
      <div className="flex gap-2 mb-4">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="border rounded px-3 py-2 flex-1"
        />
        <button
          onClick={askCrops}
          className="bg-green-600 text-white px-4 py-2 rounded"
        >
          {loading ? "Loading..." : "Ask"}
        </button>
      </div>
      {answer && (
        <div className="bg-gray-100 p-4 rounded shadow">
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}

export default Crops;
