## Calibration choices frozen before seeing planted outcomes
- G5 held-out plaintext = reference_messages.json calibration[0]; PA=CA=AZ, OP=VIG, primer=54321.
- Carter held-out plaintext = reference_messages.json calibration[1]; PA=CA=AZ, OP=VIG, key numbering AZ, direction FORWARD, key source offset 12345 in carter_az.txt.
- Both are 97 characters. Hidden true plaintext is not copied into the blind solver's input directory.
- The generator saves only the ciphertext inputs for the blind program. Evaluator, after outputs are frozen, checks rank of original plaintext among returned top100 and forward encryption.
- No replanning if one or both plants fail.
