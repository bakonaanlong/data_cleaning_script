import pandas as pd
import sys
import os

def clean_csv(input_file, output_file=None):
    try:
        # Read CSV file
        print(f"Reading file: {input_file}")
        df = pd.read_csv(input_file)
        print(f"Original shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Store original row count
        original_rows = len(df)
        
        # 1. Remove duplicate rows
        df = df.drop_duplicates()
        duplicates_removed = original_rows - len(df)
        print(f"Removed {duplicates_removed} duplicate rows")
        
        # 2. Trim whitespace from string columns
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                df[col] = df[col].str.strip()
        print("Trimmed whitespace from all text columns")
        
        # 3. Fix datatypes
        print("\nFixing datatypes...")
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    # Remove commas and currency symbols
                    cleaned = df[col].str.replace(',', '').str.replace('$', '').str.replace('€', '').str.replace('£', '')
                    numeric_col = pd.to_numeric(cleaned, errors='coerce')
                    
                    # If more than 80% converts successfully, it's numeric
                    if numeric_col.notna().sum() / len(df) > 0.8:
                        df[col] = numeric_col
                        print(f"  • {col}: converted to numeric")
                        continue
                except:
                    pass
                
                # Try to convert to datetime
                try:
                    datetime_col = pd.to_datetime(df[col], errors='coerce', infer_datetime_format=True)
                    
                    # If more than 80% converts successfully, it's datetime
                    if datetime_col.notna().sum() / len(df) > 0.8:
                        df[col] = datetime_col
                        print(f"  • {col}: converted to datetime")
                        continue
                except:
                    pass
                
                # Try to convert to boolean
                bool_values = df[col].str.lower().str.strip()
                if bool_values.isin(['true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n']).all():
                    bool_map = {
                        'true': True, 'false': False,
                        'yes': True, 'no': False,
                        '1': True, '0': False,
                        't': True, 'f': False,
                        'y': True, 'n': False
                    }
                    df[col] = bool_values.map(bool_map)
                    print(f"  • {col}: converted to boolean")
        
        # 4. Standardize entries
        for col in df.columns:
            if df[col].dtype == 'object':
                # Convert to title case for better consistency
                df[col] = df[col].str.title()
                
                # Remove extra internal whitespace
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
        print("Standardized text entries (title case, removed extra spaces)")
        
        # 5. Remove rows where all values are NaN
        df = df.dropna(how='all')
        
        # 6. Remove rows with null values if they're less than 20% of total records
        rows_before_null_removal = len(df)
        rows_with_nulls = df.isnull().any(axis=1).sum()
        null_percentage = (rows_with_nulls / rows_before_null_removal) * 100
        
        print(f"\nNull value analysis:")
        print(f"Rows with null values: {rows_with_nulls} ({null_percentage:.2f}%)")
        
        if null_percentage < 20:
            df = df.dropna()
            removed_null_rows = rows_before_null_removal - len(df)
            print(f"✓ Removed {removed_null_rows} rows with null values (below 20% threshold)")
        else:
            print(f"✗ Keeping rows with null values (exceeds 20% threshold)")
        
        # Generate output filename if not provided
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_cleaned.csv"
        
        # Save cleaned data
        df.to_csv(output_file, index=False)
        print(f"\nCleaned data saved to: {output_file}")
        print(f"Final shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        return df
        
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print("Error: The CSV file is empty.")
        sys.exit(1)
    except Exception as e:
        print(f"Error processing file: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python csv_cleaner.py <input_file.csv> [output_file.csv]")
        print("Example: python csv_cleaner.py data.csv cleaned_data.csv")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    clean_csv(input_file, output_file)

if __name__ == "__main__":
    main()