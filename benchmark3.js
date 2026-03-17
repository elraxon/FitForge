const fs = require('fs');
const html = fs.readFileSync('FitForgeV1.html', 'utf8');

const skillDataMatch = html.match(/const SKILL_DATA = (\{[\s\S]*?\n        \});/);
let SKILL_DATA = {};
if (skillDataMatch) {
    eval('SKILL_DATA = ' + skillDataMatch[1] + ';');
}

const player = {
    skills: { "Power Strike": 1 },
    stats: { STR: 10, END: 10, AGI: 10, FOC: 10 }
};

function getPlayerTotalStat(statName) {
    return player.stats[statName] || 0;
}

const iterations = 10000;
let oldTimeSum = 0;
let newTimeSum = 0;

function runOld() {
    const start = process.hrtime.bigint();
    for (let i = 0; i < iterations; i++) {
        let htmlContent = '';
        htmlContent += `<h3>Skills</h3>`;
        const skillsByClass = {};
        Object.values(SKILL_DATA).forEach(skill => {
            if (!skillsByClass[skill.class]) skillsByClass[skill.class] = [];
            skillsByClass[skill.class].push(skill);
        });

        for (const className in skillsByClass) {
            htmlContent += `<h4>${className}</h4>`;
            skillsByClass[className].sort((a,b) => a.tier - b.tier || a.name.localeCompare(b.name)).forEach(skill => {
                const currentLevel = player.skills[skill.name] || 0;
                let prereqText = "";
                let canLearn = true;
                if (skill.prerequisites) {
                    prereqText = "Req: ";
                    let reqs = [];
                    for (const pKey in skill.prerequisites) {
                        const reqValue = skill.prerequisites[pKey];
                        let isMet;
                        if (SKILL_DATA[pKey]) {
                            isMet = (player.skills[pKey] || 0) >= reqValue;
                            reqs.push(`${pKey} Lvl ${reqValue}`);
                        } else {
                            isMet = getPlayerTotalStat(pKey.toUpperCase()) >= reqValue;
                            reqs.push(`${pKey.toUpperCase()} ${reqValue}`);
                        }
                        if (!isMet && currentLevel === 0) canLearn = false;
                    }
                    prereqText += reqs.join(', ');
                }
            });
        }
    }
    const end = process.hrtime.bigint();
    return Number(end - start) / 1e6;
}

const PRECOMPUTED_SKILLS_BY_CLASS = {};
Object.values(SKILL_DATA).forEach(skill => {
    if (!PRECOMPUTED_SKILLS_BY_CLASS[skill.class]) PRECOMPUTED_SKILLS_BY_CLASS[skill.class] = [];
    PRECOMPUTED_SKILLS_BY_CLASS[skill.class].push(skill);
});
for (const className in PRECOMPUTED_SKILLS_BY_CLASS) {
    PRECOMPUTED_SKILLS_BY_CLASS[className].sort((a,b) => a.tier - b.tier || a.name.localeCompare(b.name));
}

function runNew() {
    const start = process.hrtime.bigint();
    for (let i = 0; i < iterations; i++) {
        let htmlContent = '';
        htmlContent += `<h3>Skills</h3>`;
        for (const className in PRECOMPUTED_SKILLS_BY_CLASS) {
            htmlContent += `<h4>${className}</h4>`;
            PRECOMPUTED_SKILLS_BY_CLASS[className].forEach(skill => {
                const currentLevel = player.skills[skill.name] || 0;
                let prereqText = "";
                let canLearn = true;
                if (skill.prerequisites) {
                    prereqText = "Req: ";
                    let reqs = [];
                    for (const pKey in skill.prerequisites) {
                        const reqValue = skill.prerequisites[pKey];
                        let isMet;
                        if (SKILL_DATA[pKey]) {
                            isMet = (player.skills[pKey] || 0) >= reqValue;
                            reqs.push(`${pKey} Lvl ${reqValue}`);
                        } else {
                            isMet = getPlayerTotalStat(pKey.toUpperCase()) >= reqValue;
                            reqs.push(`${pKey.toUpperCase()} ${reqValue}`);
                        }
                        if (!isMet && currentLevel === 0) canLearn = false;
                    }
                    prereqText += reqs.join(', ');
                }
            });
        }
    }
    const end = process.hrtime.bigint();
    return Number(end - start) / 1e6;
}

for(let i=0; i<5; i++) {
    oldTimeSum += runOld();
    newTimeSum += runNew();
}

console.log(`Baseline avg time: ${(oldTimeSum / 5).toFixed(2)}ms for ${iterations} iterations`);
console.log(`Optimized avg time: ${(newTimeSum / 5).toFixed(2)}ms for ${iterations} iterations`);
console.log(`Improvement: ${((oldTimeSum - newTimeSum) / oldTimeSum * 100).toFixed(2)}%`);
