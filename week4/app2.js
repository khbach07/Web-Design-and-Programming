let sample = [
    { id: 1, name: "Toán", score: 8.5 },
    { id: 2, name: "Văn", score: 8.0 },
    { id: 3, name: "Tiếng Anh", score: 9.5 },
];

let n = sample.length;

let sum = 0;

for (let i = 0; i < n; i++) {
    sum = sum + sample[i].score;
}

console.log(sum);

let highest_score = sample[0].score;

for (let i = 0; i < n; i++) {
    if (sample[i].score > highest_score) {
        highest_score = sample[i].score;
    }
}

console.log(highest_score);

let subject_above_eight = []
for (let i = 0; i < n; i++) {
    if (sample[i].score > 8) {
        subject_above_eight.push(sample[i].name);
    }
}

console.log(subject_above_eight)
