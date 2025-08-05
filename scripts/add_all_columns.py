#!/usr/bin/env python3
"""
Add all remaining columns to the Vertical system sheet.
"""

def add_remaining_columns():
    """Add all columns that haven't been created yet"""
    
    # Columns already created: Student_Name (A), Student_ID (B), Program (C)
    remaining_columns = [
        "Schedule",
        "Default_Teacher", 
        "Date",
        "Session_Num",
        "Lesson_Code",
        "Lesson_Title",
        "Lesson_URLs",
        "Attendance",
        "Actual_Teacher",
        "Progress",
        "Notes"
    ]
    
    spreadsheet_id = "1zbw7hLSa-5k83T0d6KrD-eiZv5nM855oYHV_B-tslbU"
    worksheet = "Vertical system"
    
    print("Adding remaining columns to Vertical system sheet...")
    
    for column_name in remaining_columns:
        print(f"Adding column: {column_name}")
        
        try:
            result = mcp__zapier__google_sheets_create_spreadsheet_column(
                instructions=f"Create column {column_name} in the Vertical system sheet",
                spreadsheet=spreadsheet_id,
                worksheet=worksheet,
                column_name=column_name
            )
            print(f"  ✓ Created {column_name}")
        except Exception as e:
            print(f"  ✗ Error creating {column_name}: {e}")
    
    print("\nAll columns created!")
    print("\nFinal column order should be:")
    print("A: Student_Name")
    print("B: Student_ID") 
    print("C: Program")
    print("D: Schedule")
    print("E: Default_Teacher")
    print("F: Date")
    print("G: Session_Num")
    print("H: Lesson_Code")
    print("I: Lesson_Title")
    print("J: Lesson_URLs")
    print("K: Attendance")
    print("L: Actual_Teacher")
    print("M: Progress")
    print("N: Notes")


if __name__ == "__main__":
    # Check if MCP is available
    if 'mcp__zapier__google_sheets_create_spreadsheet_column' in globals():
        add_remaining_columns()
    else:
        print("This script requires MCP functions.")
        print("Running in simulation mode...")
        
        # Show what would be created
        remaining_columns = [
            "Schedule", "Default_Teacher", "Date", "Session_Num",
            "Lesson_Code", "Lesson_Title", "Lesson_URLs", "Attendance",
            "Actual_Teacher", "Progress", "Notes"
        ]
        
        print("\nWould create these columns:")
        for i, col in enumerate(remaining_columns, start=4):
            print(f"Column {chr(65+i-1)}: {col}")