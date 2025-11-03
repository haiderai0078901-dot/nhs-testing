import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import base64
import io

# Initialize the Dash app
app = dash.Dash(__name__, title="Radiology AI Dashboard", suppress_callback_exceptions=True)
server = app.server

# Sample data generation
def generate_sample_data():
    np.random.seed(42)
    
    # Generate patient data
    patients = []
    for i in range(50):
        exam_date = datetime.now() - timedelta(days=np.random.randint(1, 365))
        follow_up_due = exam_date + timedelta(days=90)
        status = "Completed" if np.random.random() > 0.3 else "Pending"
        
        patients.append({
            'patient_id': f"P{1000 + i}",
            'name': f"Patient {i+1}",
            'age': np.random.randint(25, 85),
            'exam_type': np.random.choice(['CT Scan', 'MRI', 'X-Ray', 'Ultrasound']),
            'exam_date': exam_date.strftime('%Y-%m-%d'),
            'follow_up_due': follow_up_due.strftime('%Y-%m-%d'),
            'status': status,
            'priority': np.random.choice(['High', 'Medium', 'Low'], p=[0.2, 0.5, 0.3]),
            'ai_confidence': np.round(np.random.uniform(0.7, 0.98), 2),
            'findings': np.random.choice(['Normal', 'Suspicious', 'Critical'], p=[0.6, 0.3, 0.1])
        })
    
    return pd.DataFrame(patients)

# Generate workflow data
def generate_workflow_data():
    workflow_steps = ['Order Received', 'Image Acquisition', 'AI Analysis', 'Radiologist Review', 'Report Generation', 'Follow-up']
    data = []
    
    for step in workflow_steps:
        data.append({
            'step': step,
            'avg_duration_hours': np.random.randint(1, 48),
            'completion_rate': np.round(np.random.uniform(0.85, 0.99), 2),
            'ai_assistance': np.random.choice(['Yes', 'No'], p=[0.7, 0.3])
        })
    
    return pd.DataFrame(data)

# Load sample data
df_patients = generate_sample_data()
df_workflow = generate_workflow_data()

# Calculate metrics for the dashboard
total_patients = len(df_patients)
pending_followups = len(df_patients[df_patients['status'] == 'Pending'])
critical_cases = len(df_patients[df_patients['findings'] == 'Critical'])
avg_ai_confidence = np.round(df_patients['ai_confidence'].mean(), 2)

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("Radiology AI Workflow Dashboard", 
                style={'color': 'white', 'margin': '0', 'padding': '15px'}),
        html.Div([
            html.Span("Last updated: ", style={'color': 'white'}),
            html.Span(datetime.now().strftime("%Y-%m-%d %H:%M"), 
                     id="last-updated", style={'color': '#4cd964', 'fontWeight': 'bold'})
        ], style={'position': 'absolute', 'right': '20px', 'top': '20px'})
    ], style={'backgroundColor': '#2c3e50', 'padding': '10px', 'position': 'relative'}),
    
    # Main content
    html.Div([
        # Left sidebar - Metrics and controls
        html.Div([
            # Key Metrics
            html.Div([
                html.H3("Key Metrics", style={'color': '#2c3e50', 'borderBottom': '1px solid #ecf0f1', 'paddingBottom': '10px'}),
                
                html.Div([
                    html.Div([
                        html.H4(total_patients, style={'color': '#3498db', 'margin': '0', 'fontSize': '24px'}),
                        html.P("Total Patients", style={'margin': '0', 'color': '#7f8c8d'})
                    ], className="metric-box"),
                    
                    html.Div([
                        html.H4(pending_followups, style={'color': '#e74c3c', 'margin': '0', 'fontSize': '24px'}),
                        html.P("Pending Follow-ups", style={'margin': '0', 'color': '#7f8c8d'})
                    ], className="metric-box"),
                    
                    html.Div([
                        html.H4(critical_cases, style={'color': '#e67e22', 'margin': '0', 'fontSize': '24px'}),
                        html.P("Critical Cases", style={'margin': '0', 'color': '#7f8c8d'})
                    ], className="metric-box"),
                    
                    html.Div([
                        html.H4(avg_ai_confidence, style={'color': '#27ae60', 'margin': '0', 'fontSize': '24px'}),
                        html.P("Avg AI Confidence", style={'margin': '0', 'color': '#7f8c8d'})
                    ], className="metric-box"),
                ], style={'display': 'grid', 'gridTemplateColumns': '1fr 1fr', 'gap': '10px'}),
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px', 'marginBottom': '20px'}),
            
            # AI Controls
            html.Div([
                html.H3("AI Controls", style={'color': '#2c3e50', 'borderBottom': '1px solid #ecf0f1', 'paddingBottom': '10px'}),
                
                html.Div([
                    html.Label("AI Sensitivity:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Slider(
                        id='ai-sensitivity',
                        min=0,
                        max=100,
                        step=10,
                        value=70,
                        marks={i: f'{i}%' for i in range(0, 101, 20)},
                    ),
                ], style={'marginBottom': '15px'}),
                
                html.Div([
                    html.Label("Follow-up Threshold (days):", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Input(
                        id='followup-threshold',
                        type='number',
                        value=30,
                        min=1,
                        max=90,
                        style={'width': '100%', 'padding': '5px'}
                    ),
                ], style={'marginBottom': '15px'}),
                
                html.Button(
                    "Run AI Analysis", 
                    id="run-ai-analysis",
                    style={
                        'width': '100%', 
                        'backgroundColor': '#3498db', 
                        'color': 'white', 
                        'border': 'none', 
                        'padding': '10px', 
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
                
                html.Button(
                    "Generate Reports", 
                    id="generate-reports",
                    style={
                        'width': '100%', 
                        'backgroundColor': '#2ecc71', 
                        'color': 'white', 
                        'border': 'none', 
                        'padding': '10px', 
                        'borderRadius': '5px',
                        'marginTop': '10px',
                        'cursor': 'pointer'
                    }
                ),
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px', 'marginBottom': '20px'}),
            
            # Filters
            html.Div([
                html.H3("Filters", style={'color': '#2c3e50', 'borderBottom': '1px solid #ecf0f1', 'paddingBottom': '10px'}),
                
                html.Div([
                    html.Label("Exam Type:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='exam-type-filter',
                        options=[{'label': 'All', 'value': 'All'}] + 
                                [{'label': exam_type, 'value': exam_type} for exam_type in df_patients['exam_type'].unique()],
                        value='All',
                        clearable=False
                    ),
                ], style={'marginBottom': '15px'}),
                
                html.Div([
                    html.Label("Priority:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='priority-filter',
                        options=[{'label': 'All', 'value': 'All'}] + 
                                [{'label': priority, 'value': priority} for priority in df_patients['priority'].unique()],
                        value='All',
                        clearable=False
                    ),
                ], style={'marginBottom': '15px'}),
                
                html.Div([
                    html.Label("Findings:", style={'fontWeight': 'bold', 'marginBottom': '5px'}),
                    dcc.Dropdown(
                        id='findings-filter',
                        options=[{'label': 'All', 'value': 'All'}] + 
                                [{'label': finding, 'value': finding} for finding in df_patients['findings'].unique()],
                        value='All',
                        clearable=False
                    ),
                ]),
            ], style={'backgroundColor': 'white', 'padding': '15px', 'borderRadius': '5px'}),
        ], style={'width': '25%', 'padding': '15px', 'backgroundColor': '#ecf0f1'}),
        
        # Main content area
        html.Div([
            # Tabs for different views
            dcc.Tabs(id="tabs", value='tab-overview', children=[
                dcc.Tab(label='Dashboard Overview', value='tab-overview'),
                dcc.Tab(label='Patient Management', value='tab-patients'),
                dcc.Tab(label='Workflow Analysis', value='tab-workflow'),
                dcc.Tab(label='AI Reports', value='tab-reports'),
            ]),
            
            # Tab content
            html.Div(id='tabs-content')
        ], style={'width': '75%', 'padding': '15px'})
    ], style={'display': 'flex', 'minHeight': 'calc(100vh - 80px)'})
], style={'fontFamily': 'Arial, sans-serif'})

# Callback for tab content
@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-overview':
        return overview_tab()
    elif tab == 'tab-patients':
        return patients_tab()
    elif tab == 'tab-workflow':
        return workflow_tab()
    elif tab == 'tab-reports':
        return reports_tab()

# Overview Tab
def overview_tab():
    # Create charts for overview
    # Exam type distribution
    exam_type_fig = px.pie(df_patients, names='exam_type', title='Exam Type Distribution')
    
    # Findings by priority
    findings_fig = px.histogram(df_patients, x='findings', color='priority', 
                               title='Findings by Priority', barmode='group')
    
    # AI confidence distribution
    confidence_fig = px.histogram(df_patients, x='ai_confidence', 
                                 title='AI Confidence Distribution', nbins=10)
    
    # Workflow efficiency
    workflow_fig = px.bar(df_workflow, x='step', y='completion_rate',
                         title='Workflow Step Completion Rate',
                         color='ai_assistance')
    
    return html.Div([
        html.Div([
            html.Div([
                dcc.Graph(figure=exam_type_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '5px'}),
            
            html.Div([
                dcc.Graph(figure=findings_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '5px'}),
        ]),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=confidence_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '5px'}),
            
            html.Div([
                dcc.Graph(figure=workflow_fig)
            ], style={'width': '50%', 'display': 'inline-block', 'padding': '5px'}),
        ]),
        
        # Recent alerts
        html.Div([
            html.H3("Recent AI Alerts & Flags", style={'color': '#2c3e50', 'marginTop': '20px'}),
            html.Div([
                html.Div([
                    html.H4("Missed Follow-up", style={'color': '#e74c3c', 'margin': '0'}),
                    html.P("Patient P1005 - CT Scan from 45 days ago", style={'margin': '0', 'color': '#7f8c8d'}),
                    html.Span("High Priority", style={'color': '#e74c3c', 'fontSize': '12px', 'fontWeight': 'bold'})
                ], style={'padding': '10px', 'borderLeft': '4px solid #e74c3c', 'backgroundColor': 'white', 'marginBottom': '10px'}),
                
                html.Div([
                    html.H4("Critical Finding", style={'color': '#e67e22', 'margin': '0'}),
                    html.P("Patient P1012 - MRI shows suspicious mass", style={'margin': '0', 'color': '#7f8c8d'}),
                    html.Span("Requires Immediate Attention", style={'color': '#e67e22', 'fontSize': '12px', 'fontWeight': 'bold'})
                ], style={'padding': '10px', 'borderLeft': '4px solid #e67e22', 'backgroundColor': 'white', 'marginBottom': '10px'}),
                
                html.Div([
                    html.H4("AI Confidence Low", style={'color': '#f39c12', 'margin': '0'}),
                    html.P("Patient P1023 - X-Ray analysis confidence below threshold", style={'margin': '0', 'color': '#7f8c8d'}),
                    html.Span("Manual Review Recommended", style={'color': '#f39c12', 'fontSize': '12px', 'fontWeight': 'bold'})
                ], style={'padding': '10px', 'borderLeft': '4px solid #f39c12', 'backgroundColor': 'white'}),
            ])
        ])
    ])

# Patients Tab
def patients_tab():
    return html.Div([
        html.Div([
            html.H3("Patient Management", style={'color': '#2c3e50'}),
            html.P("Manage patient records, follow-ups, and examination results", style={'color': '#7f8c8d'}),
        ]),
        
        # Patient table
        html.Div([
            dash_table.DataTable(
                id='patient-table',
                columns=[
                    {"name": "Patient ID", "id": "patient_id"},
                    {"name": "Name", "id": "name"},
                    {"name": "Age", "id": "age"},
                    {"name": "Exam Type", "id": "exam_type"},
                    {"name": "Exam Date", "id": "exam_date"},
                    {"name": "Follow-up Due", "id": "follow_up_due"},
                    {"name": "Status", "id": "status"},
                    {"name": "Priority", "id": "priority"},
                    {"name": "AI Confidence", "id": "ai_confidence"},
                    {"name": "Findings", "id": "findings"},
                ],
                data=df_patients.to_dict('records'),
                filter_action="native",
                sort_action="native",
                page_action="native",
                page_current=0,
                page_size=10,
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontFamily': 'Arial',
                    'border': '1px solid #ecf0f1'
                },
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold'
                },
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{findings} = "Critical"'},
                        'backgroundColor': '#ffcccc',
                        'color': 'black'
                    },
                    {
                        'if': {'filter_query': '{findings} = "Suspicious"'},
                        'backgroundColor': '#fff5cc',
                        'color': 'black'
                    },
                    {
                        'if': {'filter_query': '{status} = "Pending"'},
                        'fontWeight': 'bold'
                    }
                ]
            )
        ], style={'marginTop': '20px'}),
        
        # Patient actions
        html.Div([
            html.H4("Patient Actions", style={'color': '#2c3e50', 'marginTop': '20px'}),
            html.Div([
                html.Button(
                    "Schedule Follow-up", 
                    id="schedule-followup",
                    style={
                        'backgroundColor': '#3498db', 
                        'color': 'white', 
                        'border': 'none', 
                        'padding': '10px 15px', 
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    }
                ),
                html.Button(
                    "Update EHR", 
                    id="update-ehr",
                    style={
                        'backgroundColor': '#2ecc71', 
                        'color': 'white', 
                        'border': 'none', 
                        'padding': '10px 15px', 
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    }
                ),
                html.Button(
                    "Flag for Review", 
                    id="flag-review",
                    style={
                        'backgroundColor': '#e74c3c', 
                        'color': 'white', 
                        'border': 'none', 
                        'padding': '10px 15px', 
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
            ])
        ])
    ])

# Workflow Tab
def workflow_tab():
    # Create workflow visualization
    workflow_steps = df_workflow['step'].tolist()
    completion_rates = df_workflow['completion_rate'].tolist()
    
    workflow_fig = go.Figure(go.Waterfall(
        name="Workflow",
        orientation="v",
        measure=["relative"] * len(workflow_steps),
        x=workflow_steps,
        y=completion_rates,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    workflow_fig.update_layout(
        title="Radiology Workflow Analysis",
        showlegend=True,
        height=400
    )
    
    return html.Div([
        html.Div([
            html.H3("Workflow Analysis", style={'color': '#2c3e50'}),
            html.P("Monitor and optimize radiology workflows with AI assistance", style={'color': '#7f8c8d'}),
        ]),
        
        html.Div([
            dcc.Graph(figure=workflow_fig)
        ]),
        
        # Workflow metrics table
        html.Div([
            dash_table.DataTable(
                id='workflow-table',
                columns=[
                    {"name": "Workflow Step", "id": "step"},
                    {"name": "Avg Duration (hours)", "id": "avg_duration_hours"},
                    {"name": "Completion Rate", "id": "completion_rate"},
                    {"name": "AI Assistance", "id": "ai_assistance"},
                ],
                data=df_workflow.to_dict('records'),
                style_cell={
                    'textAlign': 'left',
                    'padding': '10px',
                    'fontFamily': 'Arial',
                    'border': '1px solid #ecf0f1'
                },
                style_header={
                    'backgroundColor': '#2c3e50',
                    'color': 'white',
                    'fontWeight': 'bold'
                }
            )
        ], style={'marginTop': '20px'}),
        
        # Workflow optimization suggestions
        html.Div([
            html.H4("AI Optimization Suggestions", style={'color': '#2c3e50', 'marginTop': '20px'}),
            html.Div([
                html.Div([
                    html.H5("Reduce Image Acquisition Time", style={'color': '#3498db', 'margin': '0'}),
                    html.P("AI analysis suggests protocol optimization could reduce acquisition time by 15%", 
                          style={'margin': '5px 0', 'color': '#7f8c8d'}),
                ], style={'padding': '10px', 'borderLeft': '4px solid #3498db', 'backgroundColor': 'white', 'marginBottom': '10px'}),
                
                html.Div([
                    html.H5("Automate Report Generation", style={'color': '#2ecc71', 'margin': '0'}),
                    html.P("Implement AI-powered reporting for normal cases to reduce radiologist workload", 
                          style={'margin': '5px 0', 'color': '#7f8c8d'}),
                ], style={'padding': '10px', 'borderLeft': '4px solid #2ecc71', 'backgroundColor': 'white', 'marginBottom': '10px'}),
                
                html.Div([
                    html.H5("Prioritize Critical Cases", style={'color': '#e74c3c', 'margin': '0'}),
                    html.P("Use AI flagging to ensure critical findings are reviewed within 2 hours", 
                          style={'margin': '5px 0', 'color': '#7f8c8d'}),
                ], style={'padding': '10px', 'borderLeft': '4px solid #e74c3c', 'backgroundColor': 'white'}),
            ])
        ])
    ])

# Reports Tab
def reports_tab():
    return html.Div([
        html.Div([
            html.H3("AI-Generated Reports", style={'color': '#2c3e50'}),
            html.P("Review and customize AI-generated radiology reports", style={'color': '#7f8c8d'}),
        ]),
        
        # Report templates
        html.Div([
            html.H4("Report Templates", style={'color': '#2c3e50', 'marginTop': '20px'}),
            html.Div([
                html.Div([
                    html.H5("Standard Report", style={'color': '#3498db', 'margin': '0'}),
                    html.P("Comprehensive report with findings, impressions, and recommendations", 
                          style={'margin': '5px 0', 'color': '#7f8c8d'}),
                    html.Button(
                        "Use Template", 
                        style={
                            'backgroundColor': '#3498db', 
                            'color': 'white', 
                            'border': 'none', 
                            'padding': '5px 10px', 
                            'borderRadius': '3px',
                            'cursor': 'pointer'
                        }
                    ),
                ], style={'padding': '15px', 'border': '1px solid #ecf0f1', 'backgroundColor': 'white', 'marginRight': '10px', 'flex': '1'}),
                
                html.Div([
                    html.H5("Follow-up Report", style={'color': '#2ecc71', 'margin': '0'}),
                    html.P("Comparative analysis with previous examinations", 
                          style={'margin': '5px 0', 'color': '#7f8c8d'}),
                    html.Button(
                        "Use Template", 
                        style={
                            'backgroundColor': '#2ecc71', 
                            'color': 'white', 
                            'border': 'none', 
                            'padding': '5px 10px', 
                            'borderRadius': '3px',
                            'cursor': 'pointer'
                        }
                    ),
                ], style={'padding': '15px', 'border': '1px solid #ecf0f1', 'backgroundColor': 'white', 'marginRight': '10px', 'flex': '1'}),
                
                html.Div([
                    html.H5("Critical Findings Report", style={'color': '#e74c3c', 'margin': '0'}),
                    html.P("Urgent report for critical or suspicious findings", 
                          style={'margin': '5px 0', 'color': '#7f8c8d'}),
                    html.Button(
                        "Use Template", 
                        style={
                            'backgroundColor': '#e74c3c', 
                            'color': 'white', 
                            'border': 'none', 
                            'padding': '5px 10px', 
                            'borderRadius': '3px',
                            'cursor': 'pointer'
                        }
                    ),
                ], style={'padding': '15px', 'border': '1px solid #ecf0f1', 'backgroundColor': 'white', 'flex': '1'}),
            ], style={'display': 'flex', 'marginBottom': '20px'}),
        ]),
        
        # Report editor
        html.Div([
            html.H4("Report Editor", style={'color': '#2c3e50', 'marginTop': '20px'}),
            html.Div([
                dcc.Textarea(
                    id='report-editor',
                    value='CLINICAL HISTORY: 65-year-old female with history of breast cancer, now with back pain.\n\nCOMPARISON: None provided.\n\nTECHNIQUE: CT chest, abdomen, and pelvis without contrast.\n\nFINDINGS:\nLUNGS: Clear. No focal consolidation, mass, or effusion.\nMEDIASTINUM: Normal cardiomediastinal silhouette.\nLIVER: Normal in size and attenuation. No focal lesions.\nKIDNEYS: Normal. No hydronephrosis or stones.\nBONES: Multiple sclerotic lesions throughout the spine, consistent with metastatic disease.\n\nIMPRESSION:\nMultiple osseous metastases, stable compared to prior.\nNo new lung nodules or abdominal metastases.\n\nRECOMMENDATION:\nContinue oncologic follow-up. Consider bone scan for further evaluation if clinically indicated.',
                    style={'width': '100%', 'height': 300, 'padding': '10px', 'fontFamily': 'Arial'}
                ),
            ]),
            
            html.Div([
                html.Button(
                    "Save Report", 
                    style={
                        'backgroundColor': '#2ecc71', 
                        'color': 'white', 
                        'border': 'none', 
                        'padding': '10px 15px', 
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    }
                ),
                html.Button(
                    "Export to EHR", 
                    style={
                        'backgroundColor': '#3498db', 
                        'color': 'white', 
                        'border': 'none', 
                        'padding': '10px 15px', 
                        'borderRadius': '5px',
                        'cursor': 'pointer',
                        'marginRight': '10px'
                    }
                ),
                html.Button(
                    "AI Enhance", 
                    style={
                        'backgroundColor': '#9b59b6', 
                        'color': 'white', 
                        'border': 'none', 
                        'padding': '10px 15px', 
                        'borderRadius': '5px',
                        'cursor': 'pointer'
                    }
                ),
            ], style={'marginTop': '10px'}),
        ]),
        
        # AI suggestions for report
        html.Div([
            html.H4("AI Suggestions", style={'color': '#2c3e50', 'marginTop': '20px'}),
            html.Div([
                html.Div([
                    html.P("Consider adding specific measurements for the sclerotic lesions.", 
                          style={'margin': '0', 'color': '#7f8c8d'}),
                    html.Button(
                        "Apply Suggestion", 
                        style={
                            'backgroundColor': 'transparent', 
                            'color': '#3498db', 
                            'border': '1px solid #3498db', 
                            'padding': '2px 8px', 
                            'borderRadius': '3px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'marginTop': '5px'
                        }
                    ),
                ], style={'padding': '10px', 'border': '1px solid #3498db', 'backgroundColor': '#ebf5fb', 'marginBottom': '10px'}),
                
                html.Div([
                    html.P("Recommend follow-up in 3 months for stable metastatic disease.", 
                          style={'margin': '0', 'color': '#7f8c8d'}),
                    html.Button(
                        "Apply Suggestion", 
                        style={
                            'backgroundColor': 'transparent', 
                            'color': '#3498db', 
                            'border': '1px solid #3498db', 
                            'padding': '2px 8px', 
                            'borderRadius': '3px',
                            'cursor': 'pointer',
                            'fontSize': '12px',
                            'marginTop': '5px'
                        }
                    ),
                ], style={'padding': '10px', 'border': '1px solid #3498db', 'backgroundColor': '#ebf5fb'}),
            ])
        ])
    ])

# Callbacks for interactivity
@app.callback(
    Output('patient-table', 'data'),
    [Input('exam-type-filter', 'value'),
     Input('priority-filter', 'value'),
     Input('findings-filter', 'value')]
)
def update_patient_table(exam_type, priority, findings):
    filtered_df = df_patients.copy()
    
    if exam_type != 'All':
        filtered_df = filtered_df[filtered_df['exam_type'] == exam_type]
    
    if priority != 'All':
        filtered_df = filtered_df[filtered_df['priority'] == priority]
    
    if findings != 'All':
        filtered_df = filtered_df[filtered_df['findings'] == findings]
    
    return filtered_df.to_dict('records')

@app.callback(
    Output('last-updated', 'children'),
    [Input('run-ai-analysis', 'n_clicks'),
     Input('generate-reports', 'n_clicks')]
)
def update_last_updated(ai_clicks, report_clicks):
    return datetime.now().strftime("%Y-%m-%d %H:%M")

# Add CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #f5f7fa;
            }
            .metric-box {
                background-color: white;
                padding: 10px;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }
            .tab-content {
                padding: 15px;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

if __name__ == '__main__':
    app.run_server(debug=True)