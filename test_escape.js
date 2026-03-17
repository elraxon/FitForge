
function escapeHTML(str) {
    if (!str) return "";
    return str.replace(/[&<>"']/g, function(m) {
        return {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m];
    });
}

const testCases = [
    { input: '<script>alert("xss")</script>', expected: '&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;' },
    { input: 'John & Doe', expected: 'John &amp; Doe' },
    { input: '"quoted"', expected: '&quot;quoted&quot;' },
    { input: "O'Brian", expected: 'O&#039;Brian' }
];

testCases.forEach(test => {
    const result = escapeHTML(test.input);
    if (result === test.expected) {
        console.log(`PASS: ${test.input} -> ${result}`);
    } else {
        console.log(`FAIL: ${test.input} -> ${result} (expected: ${test.expected})`);
        process.exit(1);
    }
});
