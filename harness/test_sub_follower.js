// Tests for the pure core of sub_follower.js (fold math, mono line, auto-octave
// scoring, Follow-slot bookkeeping). No Max, no Ableton.
// Run: node --test test_sub_follower.js

const test = require("node:test");
const assert = require("node:assert");
const sf = require("./sub_follower.js");

test("fold wraps any octave into the window above the floor", () => {
    assert.strictEqual(sf.fold(28, 28), 28);
    assert.strictEqual(sf.fold(40, 28), 28);      // E an octave up
    assert.strictEqual(sf.fold(16, 28), 28);      // E an octave down
    assert.strictEqual(sf.fold(48, 28), 36);      // C lands at the top half
    assert.strictEqual(sf.fold(27, 28), 39);      // just under the floor wraps to the top
    for (let p = 0; p < 128; p++) {
        const f = sf.fold(p, 29);
        assert.ok(f >= 29 && f <= 40);
        assert.ok((f - p) % 12 === 0);            // pitch class is preserved
    }
});

test("note naming and frequency follow Ableton's C3 = 60", () => {
    assert.strictEqual(sf.noteName(60), "C3");
    assert.strictEqual(sf.noteName(28), "E0");
    assert.strictEqual(sf.noteName(21), "A-1");
    assert.ok(Math.abs(sf.noteHz(28) - 41.2) < 0.01);
    assert.ok(Math.abs(sf.noteHz(69) - 440) < 1e-9);
});

test("mono line: the lowest sounding note wins", () => {
    const line = sf.monoLine([
        { pitch: 40, start: 0, duration: 4 },
        { pitch: 36, start: 1, duration: 1 },
    ]);
    assert.deepStrictEqual(line, [
        { pitch: 40, start: 0, duration: 1 },
        { pitch: 36, start: 1, duration: 1 },
        { pitch: 40, start: 2, duration: 2 },
    ]);
});

test("mono line: layered sources on the same pitch become one note", () => {
    const line = sf.monoLine([
        { pitch: 36, start: 0, duration: 2 },
        { pitch: 36, start: 1, duration: 2 },
    ]);
    assert.deepStrictEqual(line, [{ pitch: 36, start: 0, duration: 3 }]);
});

test("mono line: a gap splits notes and empty input is empty", () => {
    const line = sf.monoLine([
        { pitch: 36, start: 0, duration: 1 },
        { pitch: 36, start: 2, duration: 1 },
    ]);
    assert.strictEqual(line.length, 2);
    assert.deepStrictEqual(sf.monoLine([]), []);
});

test("score: time outside the sweet spot costs by distance", () => {
    const line = [{ pitch: 40, start: 0, duration: 4 }];           // an E
    assert.strictEqual(sf.scoreFloor(line, 28).cost, 0);           // folds to E0, in band
    assert.strictEqual(sf.scoreFloor(line, 29).rangeCost, 2);      // folds to E1, 2 above
});

test("score: a step the fold seam turns into a leap is penalised", () => {
    const line = [
        { pitch: 36, start: 0, duration: 1 },                      // C
        { pitch: 35, start: 1, duration: 1 },                      // B, one semitone down
    ];
    assert.strictEqual(sf.scoreFloor(line, 24).jumpCost, 1);       // C0 -> B0: leap of 11
    assert.strictEqual(sf.scoreFloor(line, 28).jumpCost, 0);       // B0 -> C1: a step
});

test("chooseFloor returns the cheapest candidate, ties toward the sweet spot floor", () => {
    const stepLine = [
        { pitch: 36, start: 0, duration: 1 },
        { pitch: 35, start: 1, duration: 1 },
    ];
    const r = sf.chooseFloor(stepLine);
    assert.strictEqual(r.scores.length, sf.FLOOR_MAX - sf.FLOOR_MIN + 1);
    const min = Math.min(...r.scores.map((s) => s.cost));
    assert.strictEqual(r.scores.find((s) => s.floor === r.floor).cost, min);
    assert.strictEqual(r.floor, 28);

    // E and G in any octave: every floor up to E0 is free, so E0 wins the tie
    const eg = [
        { pitch: 52, start: 0, duration: 2 },
        { pitch: 55, start: 2, duration: 2 },
    ];
    assert.strictEqual(sf.chooseFloor(eg).floor, 28);
});

test("chooseFloor moves the seam off a riff that crosses it", () => {
    // F-minor riff walking F -> D# -> F: floor F0 would leap a seventh each time
    const riff = [
        { pitch: 41, start: 0, duration: 1 },
        { pitch: 39, start: 1, duration: 1 },
        { pitch: 41, start: 2, duration: 1 },
    ];
    const r = sf.chooseFloor(riff);
    assert.strictEqual(r.scores.find((s) => s.floor === 29).jumpCost, 1);
    assert.strictEqual(r.scores.find((s) => s.floor === r.floor).jumpCost, 0);
});

test("assignSlots keeps tracks on their Follow switch", () => {
    assert.deepStrictEqual(
        sf.assignSlots(["a", "b", null, null], ["b", "c"], 4),
        { slots: ["c", "b", null, null], overflow: [] });
    assert.deepStrictEqual(
        sf.assignSlots(undefined, ["a", "b"], 3),
        { slots: ["a", "b", null], overflow: [] });
});

test("assignSlots reports tracks that do not fit", () => {
    assert.deepStrictEqual(
        sf.assignSlots([], ["a", "b"], 1),
        { slots: ["a"], overflow: ["b"] });
});
