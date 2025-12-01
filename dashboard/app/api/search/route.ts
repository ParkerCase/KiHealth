import { NextResponse } from 'next/server';
import { buildClient } from '@xata.io/client';

const getXataClient = () => {
  const XataClient = buildClient();
  const options: any = {
    apiKey: process.env.XATA_API_KEY,
  };
  
  if (process.env.XATA_DB_URL) {
    const url = process.env.XATA_DB_URL;
    const dbMatch = url.match(/\/db\/([^:]+):(.+)$/);
    if (dbMatch) {
      const baseUrl = url.substring(0, url.lastIndexOf(':'));
      options.databaseURL = baseUrl;
      options.branch = dbMatch[2];
    } else {
      options.databaseURL = url;
    }
  }
  
  return new XataClient(options);
};

export async function POST(request: Request) {
  try {
    const { query } = await request.json();
    
    if (!query || typeof query !== 'string') {
      return NextResponse.json(
        { error: 'Query is required' },
        { status: 400 }
      );
    }

    const xata = getXataClient();
    
    // Use Xata's ask method for natural language queries
    try {
      const results = await xata.db.cancer_rankings.ask(query);
      return NextResponse.json({ success: true, results });
    } catch (askError: any) {
      // If ask fails, fall back to regular search
      console.warn('Ask method failed, falling back to search:', askError?.message);
      try {
        const searchResults = await xata.db.cancer_rankings.search(query, {
          fuzziness: 1,
          prefix: 'phrase',
        });
        return NextResponse.json({ success: true, results: searchResults, method: 'search' });
      } catch (searchError: any) {
        throw searchError;
      }
    }
  } catch (error: any) {
    console.error('Error in semantic search:', error);
    return NextResponse.json(
      { error: 'Search failed', details: error?.message },
      { status: 500 }
    );
  }
}

