import { useState } from "react";

type QueryFormProps = {
  onSubmit: (payload: {
    query_text: string | null;
    query_url: string | null;
    top_k: number;
  }) => void;
};

export default function QueryForm({ onSubmit }: QueryFormProps) {
  const [queryText, setQueryText] = useState<string>("");
  const [queryUrl, setQueryUrl] = useState<string>("");
  const [topK, setTopK] = useState<number>(5);

  const handleSubmit = () => {
    onSubmit({
      query_text: queryText || null,
      query_url: queryUrl || null,
      top_k: topK,
    });
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow space-y-4">
      <h2 className="text-xl font-semibold">Job Description Input</h2>

      <textarea
        className="w-full border p-3 rounded"
        rows={4}
        placeholder="Paste job description text..."
        value={queryText}
        onChange={(e) => setQueryText(e.target.value)}
      />

      <input
        className="w-full border p-3 rounded"
        placeholder="OR paste job description URL"
        value={queryUrl}
        onChange={(e) => setQueryUrl(e.target.value)}
      />

      <div className="flex items-center gap-4">
        <label className="font-medium">Top K:</label>

        <select
          value={topK}
          onChange={(e) => setTopK(Number(e.target.value))}
          className="border p-2 rounded"
        >
          {[5, 6, 7, 8, 9, 10].map((k) => (
            <option key={k} value={k}>
              {k}
            </option>
          ))}
        </select>

        <button
          onClick={handleSubmit}
          className="ml-auto bg-black text-white px-6 py-2 rounded hover:bg-gray-800"
        >
          Recommend
        </button>
      </div>
    </div>
  );
}
