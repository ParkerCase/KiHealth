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

export async function GET() {
  try {
    const xata = getXataClient();
    const records = await xata.db.cell_lines
      .select(['*'])
      .getAll();

    return NextResponse.json(records);
  } catch (error: any) {
    console.error('Error fetching cell lines:', error);
    return NextResponse.json(
      { error: 'Failed to fetch cell lines', details: error?.message },
      { status: error?.status || 500 }
    );
  }
}

