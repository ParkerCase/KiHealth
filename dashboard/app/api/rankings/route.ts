import { NextResponse } from 'next/server';
import { buildClient } from '@xata.io/client';

// Initialize Xata client
// Make sure XATA_API_KEY and XATA_DB_URL are set in .env.local
const getXataClient = () => {
  const XataClient = buildClient();
  
  const options: any = {
    apiKey: process.env.XATA_API_KEY,
  };
  
  // Parse database URL: remove branch from URL and pass separately
  if (process.env.XATA_DB_URL) {
    const url = process.env.XATA_DB_URL;
    // URL format: https://workspace.region.xata.sh/db/dbname:branch
    // Find the last colon (after /db/) to split database name and branch
    const dbMatch = url.match(/\/db\/([^:]+):(.+)$/);
    if (dbMatch) {
      // Remove :branch from the end of URL
      const baseUrl = url.substring(0, url.lastIndexOf(':'));
      options.databaseURL = baseUrl;
      options.branch = dbMatch[2]; // Extract branch (e.g., "main")
      console.log('Using databaseURL:', baseUrl, 'branch:', dbMatch[2]);
    } else {
      // No branch in URL, use as-is
      options.databaseURL = url;
    }
  }
  
  return new XataClient(options);
};

export async function GET() {
  try {
    // Debug: Log environment variables (without exposing full key)
    console.log('XATA_API_KEY exists:', !!process.env.XATA_API_KEY);
    console.log('XATA_API_KEY prefix:', process.env.XATA_API_KEY?.substring(0, 10));
    console.log('XATA_DB_URL:', process.env.XATA_DB_URL);
    
    const xata = getXataClient();
    const records = await xata.db.cancer_rankings
      .select([
        'Rank',
        'cancer_type',
        'n_cell_lines',
        'overall_score',
        'confidence_tier',
        'depmap_score_normalized',
        'expression_score_normalized',
        'mutation_context_score',
        'copy_number_score',
        'literature_score_normalized',
        'experimental_validation_score',
        'n_validated_cell_lines',
        'total_sl_hits',
        'has_sl_evidence',
        'STK17A_mean',
        'STK17B_mean',
        'MYLK4_mean',
        'TBK1_mean',
        'CLK4_mean',
        'Cell_Lines',
      ])
      .getAll();

    return NextResponse.json(records);
  } catch (error: any) {
    console.error('Error fetching rankings:', error);
    const errorMessage = error?.message || 'Unknown error';
    const errorStatus = error?.status || 500;
    return NextResponse.json(
      { 
        error: 'Failed to fetch rankings',
        details: errorMessage,
        status: errorStatus
      },
      { status: errorStatus }
    );
  }
}

