// Federal state code to abbreviation mapping
export const FEDERAL_STATE_ABBREVIATIONS: Record<string, string> = {
  'BW': 'BW', // Baden-Württemberg
  'BY': 'BY', // Bayern
  'BE': 'BE', // Berlin
  'BB': 'BB', // Brandenburg
  'HB': 'HB', // Bremen
  'HH': 'HH', // Hamburg
  'HE': 'HE', // Hessen
  'MV': 'MV', // Mecklenburg-Vorpommern
  'NI': 'NI', // Niedersachsen
  'NW': 'NW', // Nordrhein-Westfalen
  'RP': 'RP', // Rheinland-Pfalz
  'SL': 'SL', // Saarland
  'SN': 'SN', // Sachsen
  'ST': 'ST', // Sachsen-Anhalt
  'SH': 'SH', // Schleswig-Holstein
  'TH': 'TH', // Thüringen
};

// Federal state code to full name mapping
export const FEDERAL_STATE_NAMES: Record<string, string> = {
  'BW': 'Baden-Württemberg',
  'BY': 'Bayern',
  'BE': 'Berlin',
  'BB': 'Brandenburg',
  'HB': 'Bremen',
  'HH': 'Hamburg',
  'HE': 'Hessen',
  'MV': 'Mecklenburg-Vorpommern',
  'NI': 'Niedersachsen',
  'NW': 'Nordrhein-Westfalen',
  'RP': 'Rheinland-Pfalz',
  'SL': 'Saarland',
  'SN': 'Sachsen',
  'ST': 'Sachsen-Anhalt',
  'SH': 'Schleswig-Holstein',
  'TH': 'Thüringen',
};

/**
 * Get the abbreviation for a federal state code or name
 */
export const getFederalStateAbbreviation = (codeOrName: string): string => {
  // First try as code
  if (FEDERAL_STATE_ABBREVIATIONS[codeOrName]) {
    return FEDERAL_STATE_ABBREVIATIONS[codeOrName];
  }
  
  // Then try to find by full name
  const foundCode = Object.keys(FEDERAL_STATE_NAMES).find(
    code => FEDERAL_STATE_NAMES[code] === codeOrName
  );
  
  if (foundCode) {
    return FEDERAL_STATE_ABBREVIATIONS[foundCode];
  }
  
  // Fallback: return the input
  return codeOrName;
};

/**
 * Get the full name for a federal state code
 */
export const getFederalStateName = (code: string): string => {
  return FEDERAL_STATE_NAMES[code] || code;
};

/**
 * Format federal state codes as abbreviations for display
 */
export const formatFederalStates = (codes: string[]): string => {
  if (codes.length === 0) return '';
  
  const abbreviations = codes
    .map(code => getFederalStateAbbreviation(code))
    .sort(); // Sort alphabetically for consistent display
  
  return abbreviations.join(', ');
};
