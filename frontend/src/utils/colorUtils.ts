/**
 * Helper module for color calculations and manipulations
 */

/**
 * Calculates the best contrasting text color (black or white) for a given background hex color.
 * Uses the YIQ equation for perceived brightness.
 * 
 * @param hexColor Background color in hex format (e.g. "#FFFFFF", "#fff", "FFFFFF")
 * @returns "#000000" (black) or "#FFFFFF" (white) depending on contrast
 */
export function getTextColorForBackground(hexColor: string | undefined): '#000000' | '#FFFFFF' {
    if (!hexColor) return '#FFFFFF';

    // Strip '#' if present
    let hex = hexColor.replace('#', '');

    // Handle 3-character hex codes
    if (hex.length === 3) {
        hex = hex.split('').map(char => char + char).join('');
    }

    // Fallback to white if invalid hex
    if (hex.length !== 6) return '#FFFFFF';

    // Parse RGB
    const r = parseInt(hex.substring(0, 2), 16);
    const g = parseInt(hex.substring(2, 4), 16);
    const b = parseInt(hex.substring(4, 6), 16);

    // If parsing failed
    if (isNaN(r) || isNaN(g) || isNaN(b)) return '#FFFFFF';

    // Calculate relative luminance (using the YIQ formula)
    const yiq = (r * 299 + g * 587 + b * 114) / 1000;

    // Return black for light backgrounds, white for dark backgrounds
    return yiq >= 128 ? '#000000' : '#FFFFFF';
}
