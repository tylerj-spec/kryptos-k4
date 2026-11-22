#!/usr/bin/env python3
"""Independent synthetic reference: event clock and enumeration of complete keys.

This file is not imported by the target runner. It contains no K4 input or
published observation list. The toy oracle tries every wiring; it never uses
the production equality-conflict criterion.
"""
from itertools import permutations


def event_clock(length, n, phase, direction):
    assert n >= 1 and 0 <= phase < n and direction in (-1, 1)
    remaining, angle = n-phase, 0
    offsets = []
    for _ in range(length):
        offsets.append(angle)
        remaining -= 1
        if remaining == 0:
            angle += direction
            remaining = n
    return offsets


def encrypt(text, wiring, input_alphabet, output_alphabet, n, phase, direction):
    return encrypt_offsets(text, wiring, input_alphabet, output_alphabet,
                           event_clock(len(text), n, phase, direction))


def encrypt_offsets(text, wiring, input_alphabet, output_alphabet, offsets):
    q = len(wiring)
    assert sorted(wiring) == list(range(q))
    assert len(set(input_alphabet)) == len(set(output_alphabet)) == q
    result = []
    assert len(text) == len(offsets)
    for letter, angle in zip(text, offsets):
        # Rotate explicit contact lists rather than reuse the floor-formula map.
        pin = input_alphabet.index(letter)
        input_contact = list(range(q))[angle % q:] + list(range(q))[:angle % q]
        source = input_contact[pin]
        out_contact = wiring[source]
        symbol_index = input_contact.index(out_contact)
        result.append(output_alphabet[symbol_index])
    return "".join(result)


def decrypt(ciphertext, wiring, input_alphabet, output_alphabet, n, phase, direction):
    q = len(wiring)
    result = []
    for letter, angle in zip(ciphertext, event_clock(len(ciphertext), n, phase, direction)):
        rotated = list(range(q))[angle % q:] + list(range(q))[:angle % q]
        output_contact = rotated[output_alphabet.index(letter)]
        input_contact = wiring.index(output_contact)
        result.append(input_alphabet[rotated.index(input_contact)])
    return "".join(result)


def brute_pair_verdict(q, pairs):
    """Return exact feasibility and all one-observation omissions via all q! keys."""
    exact, possible_deletions = False, 0
    all_deletions = (1 << len(pairs)) - 1
    for wiring in permutations(range(q)):
        wrong = [j for j, (x, y) in enumerate(pairs) if wiring[x] != y]
        if not wrong:
            exact, possible_deletions = True, all_deletions
            break
        if len(wrong) == 1:
            possible_deletions |= 1 << wrong[0]
    return exact, possible_deletions


def reference_pairs(plaintext, ciphertext, positions, input_alphabet,
                    output_alphabet, n, phase, direction):
    q = len(input_alphabet)
    offsets = event_clock(len(ciphertext), n, phase, direction)
    return [((input_alphabet.index(plaintext[j]) + offsets[j]) % q,
             (output_alphabet.index(ciphertext[j]) + offsets[j]) % q)
            for j in positions]
