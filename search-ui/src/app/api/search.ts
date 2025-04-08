// src/app/api/search.ts
import { NextApiRequest, NextApiResponse } from 'next';

const searchHandler = async (req: NextApiRequest, res: NextApiResponse) => {
  const { q } = req.query; // Extract search query from the URL

  if (!q || typeof q !== 'string') {
    return res.status(400).json({ error: 'Invalid search query' });
  }

  try {
    // Example: Fetch data based on the query (you can replace this with actual data fetching logic)
    const results = await searchDatabase(q);

    return res.status(200).json(results); // Send the search results back as JSON
  } catch (error) {
    return res.status(500).json({ error: 'Internal server error' });
  }
};

// Mock function to simulate a search in a database or API
const searchDatabase = async (query: string) => {
  // Example data: Replace with your actual search logic
  const data = [
    { name: 'Apple' },
    { name: 'Banana' },
    { name: 'Orange' },
  ];
  
  return data.filter(item => item.name.toLowerCase().includes(query.toLowerCase()));
};

export default searchHandler;
