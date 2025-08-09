
# MCP Upload Instructions for 10-Parameter Model

## Step 1: Create Spreadsheet
Use: mcp__zapier__google_sheets_create_spreadsheet
Title: Telebort_Core_Params_20250810
Headers: student_id,session_date,program_code,lesson_topic,progress_status,attendance_status,session_teacher,data_confidence,quality

## Step 2: Add Main Data (in batches of 100)
Total rows to upload: 4525

## Step 3: Create Dashboard Sheet
Use: mcp__zapier__google_sheets_create_worksheet
Title: Dashboard
Headers: Metric,Value,Percentage,Status,Last_Updated

## Step 4: Add Dashboard Metrics
9 rows of metrics

## Step 5: Create At-Risk Students Sheet
Identify and list students with:
- 3+ consecutive absences
- Multiple incomplete lessons
- Low data confidence

## Step 6: Share Spreadsheet
Use: mcp__zapier__google_drive_add_file_sharing_preference
Permission: anyone_with_link_can_view
