def process_gpt_result_for_bills(result: str):
    valid_keys = ['receipt_id', 'merchant_name', 'date', 'total_amount', 'currency', 'alcohol', 'document_type']

    details = {"is_valid_document": False}
    output = []
    result = result.translate(str.maketrans('','', '*"'))

    if 'document_type' in result:
        details['is_valid_document'] = True
        # Split the string by newline character to get individual lines
        lines = result.split('\n')
        # Iterate over each line
        for line in lines:
            # Split each line by ':' to separate key and value
            parts = line.split(':')

            # Ensure there are two parts (key and value)
            if len(parts) == 2:
                # Strip any leading or trailing whitespace
                key = parts[0].strip()
                value = parts[1].strip()

                for valid_key in valid_keys:
                    if valid_key in key:
                        # Add key-value pair to the dictionary
                        if valid_key == 'document_type' and any(ele in value.lower() for ele in ['other', 'resume']):
                            details['is_valid_document'] = False

                        details[valid_key] = value

    output.append(details)
    return output