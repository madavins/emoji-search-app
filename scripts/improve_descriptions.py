from google import genai
import os
import json
import time
from dotenv import load_dotenv
import sys 

INPUT_FILENAME = "data/emoji_data.json"
OUTPUT_FILENAME = "data/emoji_data_augmented.json"
API_KEY_ENV_VAR = "GEMINI_API_KEY"
MODEL_NAME = "gemini-2.5-pro-preview-03-25" #gemini-2.5-flash-preview-04-17 is also good
RATE_LIMIT_DELAY_SECONDS = 1.5
CHECKPOINT_FREQUENCY = 50 

# prompt to generate the augmented descriptions
PROMPT_TEMPLATE = """
Emoji: '{emoji}'
Original name: '{original_description}'

Task: Generate one single, concise sentence describing the emoji and its core semantic meaning. This sentence will be used to generate embeddings for semantic search.

Instructions:
- The sentence must capture the primary meaning/symbolism and key relevant keywords/ideas.
- Be direct and factual.
- DO NOT repeat the input emoji '{emoji}' in the output sentence.
- DO NOT use introductory phrases like "This emoji represents...". Directly start with the description.

Description (one sentence):
"""

def save_data(data, filename):
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return True
    except Exception as e:
        print(f"\nError saving checkpoint to {filename}: {e}")
        return False

def enrich_emoji_data():
    """
    Loads original emoji data extracted from emoji library, uses the Gemini API to 
    generate enriched descriptions,saves progress periodically, and handles resuming
    from checkpoints.
    """

    load_dotenv()
    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        print(f"Error: Environment variable {API_KEY_ENV_VAR} not found.")
        sys.exit(1)

    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Gemini client: {e}")
        sys.exit(1)

    try:
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
            input_data = json.load(f)
        print(f"Loaded {len(input_data)} total emojis.")
    except Exception as e:
        print(f"Error loading input data from {INPUT_FILENAME}: {e}")
        sys.exit(1)

    augmented_data = []
    processed_emojis = set()
    if os.path.exists(OUTPUT_FILENAME):
        try:
            # load existing data to support resuming interrupted processing
            with open(OUTPUT_FILENAME, 'r', encoding='utf-8') as f:
                augmented_data = json.load(f)
            for item in augmented_data:
                if 'emoji' in item:
                    processed_emojis.add(item['emoji'])
            print(f"Resuming. Already processed {len(processed_emojis)} emojis.")
        except Exception:
            # reset data structures if output file exists but can't be parsed
            augmented_data = []
            processed_emojis = set()

    total_emojis_to_process = len(input_data)
    newly_processed_count = 0
    skipped_count = 0
    error_count = 0

    print(f"\nStarting enrichment loop for {total_emojis_to_process} emojis...")
    
    remaining_count = total_emojis_to_process - len(processed_emojis)
    if remaining_count > 0:
        print(f"Need to process {remaining_count} more emojis.")

    for index, emoji_obj in enumerate(input_data):
        emoji = emoji_obj['emoji']
        original_description = emoji_obj['description']

        # skip already processed emojis when resuming
        if emoji in processed_emojis:
            continue

        print(f"Processing {index + 1}/{total_emojis_to_process}: {emoji} ({original_description})... ", end='', flush=True)

        new_emoji_obj = emoji_obj.copy()
        formatted_prompt = PROMPT_TEMPLATE.format(emoji=emoji, original_description=original_description)

        try:
            response = client.models.generate_content(
                model=f"models/{MODEL_NAME}",
                contents=[formatted_prompt]
            )

            # handle potential issues with the response
            if response.prompt_feedback and response.prompt_feedback.block_reason:
                reason = response.prompt_feedback.block_reason
                print(f"Skipped (Blocked: {reason}).")
                new_emoji_obj['augmented_description'] = f"Skipped - Blocked by API ({reason})"
                skipped_count += 1
            elif not response.candidates or response.candidates[0].finish_reason.name != "STOP":
                reason = response.candidates[0].finish_reason.name if response.candidates else "NO_CANDIDATES"
                print(f"Skipped (Reason: {reason}).")
                new_emoji_obj['augmented_description'] = f"Skipped - Generation issue ({reason})"
                skipped_count += 1
            elif hasattr(response, 'text') and response.text:
                augmented_description = response.text.strip()
                new_emoji_obj['augmented_description'] = augmented_description
                print("Success.")
            else:
                print("Warning: Could not extract text.")
                new_emoji_obj['augmented_description'] = "Warning - Could not extract text."
                skipped_count += 1

        except Exception as e:
            print(f"Error! ({type(e).__name__}: {e})")
            new_emoji_obj['augmented_description'] = f"Error - API call failed: {e}"
            error_count += 1

        augmented_data.append(new_emoji_obj)
        processed_emojis.add(emoji)
        newly_processed_count += 1

        is_last_item = (index == total_emojis_to_process - 1)
        if (newly_processed_count > 0 and newly_processed_count % CHECKPOINT_FREQUENCY == 0) or is_last_item:
            print(f"\nCheckpointing... (Processed {newly_processed_count} new items in this run)", end=' ', flush=True)
            if save_data(augmented_data, OUTPUT_FILENAME):
                print("Saved.")
            else:
                print("Save FAILED.")

        if not is_last_item:
            time.sleep(RATE_LIMIT_DELAY_SECONDS)

    total_in_output = len(augmented_data)
    success_count = total_in_output - skipped_count - error_count
    print(f"Summary: Total in output file={total_in_output}, Success={success_count}, Skipped={skipped_count}, Errors={error_count}")

    if save_data(augmented_data, OUTPUT_FILENAME):
        print("Final data saved successfully.")

if __name__ == "__main__":
    enrich_emoji_data()