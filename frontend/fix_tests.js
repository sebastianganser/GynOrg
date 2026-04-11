const fs = require('fs');
const path = require('path');

const files = [
    path.join(__dirname, 'src/stores/__tests__/calendarFilterStore.test.ts'),
    path.join(__dirname, 'src/hooks/__tests__/useFilteredCalendarEvents.test.ts'),
    path.join(__dirname, 'src/utils/__tests__/calendarFilters.test.ts')
];

for (const file of files) {
    let content = fs.readFileSync(file, 'utf8');

    // Remove simple assertions and toggles
    content = content.replace(/.*show(VacationAbsences|SickLeave|Training|SpecialLeave).*\n/g, '');
    content = content.replace(/.*toggle(VacationAbsences|SickLeave|Training|SpecialLeave).*\n/g, '');

    // Fix getActiveFilterCount assertions
    content = content.replace(/expect\(getActiveFilterCount\(filters\)\)\.toBe\(6\);/g, 'expect(getActiveFilterCount(filters)).toBe(2);');
    content = content.replace(/expect\(getActiveFilterCount\(filters\)\)\.toBe\(3\);/g, 'expect(getActiveFilterCount(filters)).toBe(1);');

    fs.writeFileSync(file, content);
}
console.log('Fixed.');
