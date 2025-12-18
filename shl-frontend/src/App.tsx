import { useState } from "react";
import QueryForm from "./components/QueryForm";
import ResultsTable from "./components/ResultsTable";

const API_BASE = "http://127.0.0.1:8000";

type RecommendResponse = {
  table: Array<Record<string, string | number | null>>;
};

type RecommendPayload = {
  query_text: string | null;
  query_url: string | null;
  top_k: number;
};

export default function App() {
  const [results, setResults] = useState<RecommendResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const handleSubmit = async (payload: RecommendPayload) => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/recommend`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Request failed");
      }

      const data: RecommendResponse = await res.json();
      setResults(data);
    } catch (err) {
      alert((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-10">
      <h1 className="text-3xl font-bold mb-6">
        SHL Assessment Recommendation System
      </h1>

      <QueryForm onSubmit={handleSubmit} />

      {loading && <p className="mt-4">Loading...</p>}

      <ResultsTable data={results} />
    </div>
  );
}
