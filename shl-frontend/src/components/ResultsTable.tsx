type ResultsTableProps = {
  data: {
    table: Array<Record<string, string | number | null>>;
  } | null;
};

export default function ResultsTable({ data }: ResultsTableProps) {
  if (!data?.table || data.table.length === 0) return null;

  return (
    <div className="mt-6 bg-white rounded-xl shadow overflow-x-auto">
      <table className="w-full border-collapse">
        <thead className="bg-gray-100">
          <tr>
            {Object.keys(data.table[0]).map((key) => (
              <th key={key} className="p-3 text-left border">
                {key}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.table.map((row, i) => (
            <tr key={i} className="hover:bg-gray-50">
              {Object.values(row).map((val, j) => (
                <td key={j} className="p-3 border text-sm">
                  {val ?? "N/A"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
