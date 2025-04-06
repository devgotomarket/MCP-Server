import * as cheerio from 'cheerio';

/**
 * Extracts content from a web page
 * 
 * @param url - The URL of the web page to extract content from
 * @returns The extracted and cleaned text content
 */
export async function extractWebContent(url: string): Promise<string> {
  try {
    // Validate URL format
    if (!url.match(/^(https?:\/\/)/i)) {
      throw new Error('Invalid URL format. URL must start with http:// or https://');
    }
    
    // Fetch the content from the URL
    const response = await fetch(url);
    
    // Check if the fetch was successful
    if (!response.ok) {
      throw new Error(`Failed to fetch content: ${response.status} ${response.statusText}`);
    }
    
    // Get the HTML content
    const html = await response.text();
    
    // Use cheerio to parse and clean the HTML
    const $ = cheerio.load(html);
    
    // Extract the page title
    const title = $('title').text().trim();
    
    // Remove scripts, styles, and other non-content elements
    $('script, style, nav, header, footer, iframe, noscript').remove();
    
    // Look for main content areas
    let mainContent = $('main, article, [role="main"], .content, #content');
    
    // If no specific content container found, use body
    if (mainContent.length === 0) {
      mainContent = $('body');
    }
    
    // Extract text and clean it up
    let text = mainContent.text();
    
    // Clean up whitespace
    text = text.replace(/\s+/g, ' ')
               .replace(/\n\s*\n/g, '\n\n')
               .trim();
    
    // Format with title
    return `Title: ${title}\n\n${text}`;
    
  } catch (error) {
    if (error instanceof Error) {
      throw error;
    } else {
      throw new Error('An unknown error occurred while extracting web content');
    }
  }
}