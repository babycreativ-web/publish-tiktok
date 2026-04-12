from voice import generate_full_voice

full_text = "He was rejected 100 times.\nNo one believed in his vision.\nHe worked while everyone else slept.\nToday, he runs a global empire.\nNever stop entirely..."

print("Testing generate_full_voice directly with 'adam'...")
import os; os.makedirs("temp", exist_ok=True)
generate_full_voice(full_text, "adam")
