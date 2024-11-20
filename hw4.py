import sys
import data
import csv
import build_data
import county_demographics
from typing import List, Dict

# Function to load data from the CORGIS dataset
def load_data() -> List[data.CountyDemographics]:
    counties = []
    try:
        with open('county_demographics.csv', mode='r') as file:
            reader = csv.DictReader(file)
            # Iterate through each row and create a CountyDemographics object
            for entry in reader:
                counties.append(data.CountyDemographics(
                    age=entry['Age'], # Assign demographic fields
                    county=entry['County'],
                    education=entry['Education'],
                    ethnicities=entry['Ethnicities'],
                    income=entry['Income'],
                    population={'2014 Population': int(entry['Population'])},  # Assuming Population is a number
                    state=entry['State']
                ))
    except FileNotFoundError:
        print("Error: 'county_demographics.csv' not found.")
        return []
    except Exception as e:
        print(f"Error reading the data: {e}")
        return []

    print(f"Loaded {len(counties)} county entries")
    return counties

# Supported operations
def display(counties: List[data.CountyDemographics]):
    #Displays the county name, state, and 2014 population for each county.
    for county in counties:
        print(f"{county.county}, {county.state}: {county.population['2014 Population']} people")

def filter_state(counties: List[data.CountyDemographics], state: str) -> List[data.CountyDemographics]:
    filtered = [c for c in counties if c.state == state]
    print(f"Filter: state == {state} ({len(filtered)} entries)")
    return filtered

def filter_gt(counties: List[data.CountyDemographics], field: str, threshold: float) -> List[data.CountyDemographics]:
    filtered = [c for c in counties if field_in_county(c, field) > threshold]
    print(f"Filter: {field} gt {threshold} ({len(filtered)} entries)")
    return filtered

def filter_lt(counties: List[data.CountyDemographics], field: str, threshold: float) -> List[data.CountyDemographics]:
    filtered = [c for c in counties if field_in_county(c, field) < threshold]
    print(f"Filter: {field} lt {threshold} ({len(filtered)} entries)")
    return filtered

def population_total(counties: List[data.CountyDemographics]):
    total = sum(c.population['2014 Population'] for c in counties)
    print(f"2014 population: {total}")

def population_field(counties: List[data.CountyDemographics], field: str):
    total = sum(c.population['2014 Population'] * (field_in_county(c, field) / 100) for c in counties)
    print(f"2014 {field} population: {total}")

def percent_field(counties: List[data.CountyDemographics], field: str):
    total_population = sum(c.population['2014 Population'] for c in counties)
    sub_population = sum(c.population['2014 Population'] * (field_in_county(c, field) / 100) for c in counties)
    percentage = (sub_population / total_population) * 100
    print(f"2014 {field} percentage: {percentage}")

def field_in_county(county: data.CountyDemographics, field: str) -> float:
    sections = field.split('.')
    data = county
    for section in sections:
        data = getattr(data, section.lower())
    return data

# Main program
def main():
    if len(sys.argv) != 2:
        print("Error: Please provide an operations file.")
        return

    operations_file = sys.argv[1]
    try:
        with open(operations_file, 'r') as file:
            operations = file.readlines()
    except FileNotFoundError:
        print(f"Error: Could not open {operations_file}")
        return

    counties = load_data()
    print(f"Loaded {len(counties)} county entries")

    for line_num, operation in enumerate(operations, start=1):
        operation = operation.strip()
        if not operation or operation.startswith("#"):
            continue

        try:
            parts = operation.split(':')
            op_type = parts[0]
            if op_type == "display":
                display(counties)
            elif op_type == "filter-state":
                counties = filter_state(counties, parts[1])
            elif op_type == "filter-gt":
                counties = filter_gt(counties, parts[1], float(parts[2]))
            elif op_type == "filter-lt":
                counties = filter_lt(counties, parts[1], float(parts[2]))
            elif op_type == "population-total":
                population_total(counties)
            elif op_type == "population":
                population_field(counties, parts[1])
            elif op_type == "percent":
                percent_field(counties, parts[1])
            else:
                raise ValueError("Unknown operation")
        except Exception as e:
            print(f"Error in line {line_num}: {e}")

if __name__ == "__main__":
    main()
