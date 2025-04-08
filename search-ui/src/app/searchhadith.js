import React, { useState } from 'react';
import axios from 'axios';

const SearchHadith = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/search?query=${query}`);
      setResults(response.data.results);
    } catch (error) {
      console.error("Error fetching data:", error);
    }
  };

  return (
    <div>
      <h1>Search Hadith</h1>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search for Hadith"
      />
      <button onClick={handleSearch}>Search</button>

      <div>
        {results.length > 0 ? (
          <ul>
            {results.map((result) => (
              <li key={result.id}>
                <h2>{result.hadith_id}</h2>
                <p>{result.text_en}</p>
                <p><strong>Source:</strong> {result.source}</p>
                <p><strong>Chapter:</strong> {result.chapter}</p>
              </li>
            ))}
          </ul>
        ) : (
          <p>No results found.</p>
        )}
      </div>
    </div>
  );
};

export default SearchHadith;
