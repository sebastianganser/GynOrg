---
description: Systematic approach for debugging CSS layout and sizing issues to avoid wasting tokens
globs: **/*.css, **/*.tsx, **/*.jsx, **/*.html
alwaysApply: true
---

# CSS Layout/Sizing Problem Debugging Protocol

When encountering layout problems (scrollbars, clipping, sizing issues, overflow):

## 1. STOP - Don't Guess!

- ❌ **DON'T** make assumptions about the cause
- ❌ **DON'T** try multiple "quick fixes" hoping one works
- ❌ **DON'T** modify random CSS properties
- ✅ **DO** follow the systematic debugging process below

## 2. Request Browser DevTools Inspection FIRST

**Always ask the user to inspect the problem area:**

> "Kannst du mit Rechtsklick > Untersuchen den betroffenen Bereich öffnen und einen Screenshot vom Elements/Computed Tab machen?"

Or in English:
> "Can you right-click > Inspect the affected area and share a screenshot of the Elements/Computed tab?"

## 3. Analyze the Inspection Results

Look for these common culprits in the Computed/Styles tabs:

### Height/Width Issues:
- `height: [fixed-value]px` → Should often be `100%`, `auto`, or `flex: 1`
- `max-height: [value]` → May be restricting growth
- `min-height: [value]` → May be forcing unnecessary space

### Overflow Issues:
- `overflow: auto` or `overflow-y: auto` → Causing scrollbars
- `overflow: hidden` → Clipping content
- Nested containers with conflicting overflow settings

### Spacing Issues:
- `padding` or `margin` → Reducing available space
- `gap` in flex/grid → Adding unexpected spacing

### Container Issues:
- Multiple nested `div` containers with conflicting sizing
- Flexbox/Grid parent without proper `flex: 1` or `height: 100%` on children

## 4. Search CSS Files Systematically

Before making changes, search for the problematic properties:

```bash
# Search for fixed heights
rg "height:\s*\d+px" --type css

# Search for overflow properties
rg "overflow(-y)?:\s*(auto|scroll)" --type css

# Search for max-height restrictions
rg "max-height:\s*\d+" --type css

# Search for specific class names seen in DevTools
rg "\.custom-month-view" --type css
```

## 5. Make ONE Targeted Change at a Time

- ✅ Change the SPECIFIC property identified in DevTools
- ✅ Verify with user before proceeding to next change
- ✅ Document what you changed and why

## 6. Common Solutions

### Problem: Scrollbar appears, content is clipped
**Check for:**
- Fixed `height` values → Change to `100%` or remove
- `overflow: auto` → Change to `hidden` or remove
- Parent container without `flex: 1` or `height: 100%`

### Problem: Container too small
**Check for:**
- `max-height` restrictions → Increase or remove
- Missing `flex: 1` on flex children
- Missing `height: 100%` in nested containers

### Problem: Container too large
**Check for:**
- `min-height` forcing size → Reduce or remove
- Padding/margin adding unexpected space

## Example: The Right Way

```typescript
// User reports: "Calendar has scrollbar and bottom is cut off"

// ❌ WRONG approach:
// - Try changing container height to 1100px
// - Try adding overflow: hidden to parent
// - Try removing padding
// - Try changing flex properties
// (Wasting tokens on guesses)

// ✅ RIGHT approach:
// 1. Ask user to inspect the calendar element
// 2. User shares screenshot showing: .custom-month-view { height: 600px; overflow-y: auto; }
// 3. Change ONLY those two properties: height: 100%; overflow-y: hidden;
// 4. Problem solved in ONE change
```

## Remember

**Browser DevTools inspection is FREE - token usage is NOT.**

Always inspect first, change second.
