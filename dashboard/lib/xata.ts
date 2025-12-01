import { buildClient } from '@xata.io/client';

// Initialize Xata client
// Make sure to set XATA_API_KEY and XATA_DB_URL in your .env.local file
export const getXataClient = () => {
  if (!process.env.XATA_API_KEY) {
    throw new Error('XATA_API_KEY is not set in environment variables');
  }
  
  const XataClient = buildClient();
  
  if (process.env.XATA_DB_URL) {
    return new XataClient({
      apiKey: process.env.XATA_API_KEY,
      databaseURL: process.env.XATA_DB_URL,
    });
  } else {
    return new XataClient({
      apiKey: process.env.XATA_API_KEY,
      branch: process.env.XATA_BRANCH || 'main',
    });
  }
};

