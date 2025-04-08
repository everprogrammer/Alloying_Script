import re

def parse_composition(composition_text):
    composition_dict = {}
    # This pattern matches element, percentage, and ignores the target part
    # Case-insensitive for "Target/target" and handles different status indicators
    pattern = r'([A-Za-z]+):\s*([0-9.]+)%\s*\([Tt]arget:.*?\)'
    
    # Split the text into lines and process each line
    for line in composition_text.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Skip lines with "No target specified"
        if "(No target specified)" in line:
            continue
            
        # Process lines with target information (regardless of status indicators)
        match = re.search(pattern, line)
        if match:
            element = match.group(1)
            percentage = float(match.group(2))
            composition_dict[element] = percentage
                
    return composition_dict

# Sample 
sample = """
Final composition:
Al: 91.7782% (Target: 85.0-90.0%) ⚠️ Outside target
Si: 5.4577% (Target: 11.0-13.0%) ⚠️ Outside target
Cu: 3.7353% (Target: 0.0-1%) ⚠️ Outside target
Fe: 0.3294% (Target: 0.0-1.3%) ✅ Within target
Pb: 0.0792% (Target: 0.0-0.15%) ✅ Within target
Mn: 0.0427% (Target: 0.0-0.35%) ✅ Within target
Zn: 0.0309% (Target: 0.0-0.5%) ✅ Within target
Ti: 0.0133% (Target: 0.0-0.2%) ✅ Within target
Ni: 0.0061% (Target: 0.0-0.5%) ✅ Within target
Sn: 0.0033% (Target: 0.0-0.15%) ✅ Within target
Cr: 0.0026% (Target: 0.0-0.15%) ✅ Within target
Mg: 0.0000% (Target: 0.0-0.1%) ✅ Within target 
"""

# Process samples
dictionary = parse_composition(sample)

print("composition=" , dictionary)
