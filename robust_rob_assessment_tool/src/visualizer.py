# src/visualizer.py

import pandas as pd
import logging
import json
import os
import re

logger = logging.getLogger(__name__)

class ROBVisualizer:
    """
    Generates an interactive HTML visualization for ROB assessment results.
    """
    def __init__(self, config: dict):
        self.config = config
        self.model_names = [model['name'] for model in config['llm_models']]
        # Define the order of domains
        self.core_domains = [
            "1. Random sequence generation", "2. Allocation concealment",
            "3. Blinding of participants", "4. Blinding of healthcare providers",
            "5. Blinding of outcome assessors", "6. Outcome data not included in analysis"
        ]
        self.optional_domains = [
            "7. Balance of baseline prognostic factors", "8. Balance of co-interventions in blinded trials",
            "9. Different outcome assessment between groups", "10. Different follow-up between groups",
            "11. Validity of outcome measurement methods", "12. As-treated analysis concerns",
            "13. Selective outcome reporting", "14. Early trial termination for benefit"
        ]

    def generate_visualization(self, excel_path: str, output_html_path: str):
        """
        Main function to load data, process it, and generate the HTML file.
        """
        logger.info(f"Reading assessment data from {excel_path}...")
        try:
            df = self._load_data(excel_path)
            if df is None:
                return
            
            logger.info("Processing data for visualization...")
            processed_data = self._process_data(df)
            
            logger.info(f"Generating HTML visualization file at {output_html_path}...")
            html_content = self._generate_html(processed_data)
            
            with open(output_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"Successfully created visualization: {output_html_path}")

        except Exception as e:
            logger.error(f"Failed to generate visualization: {e}", exc_info=True)

    def _load_data(self, excel_path: str) -> pd.DataFrame | None:
        """Loads the 'Integrated Results' sheet from the Excel file."""
        if not os.path.exists(excel_path):
            logger.error(f"Excel file not found at {excel_path}. Cannot generate visualization.")
            return None
        try:
            return pd.read_excel(excel_path, sheet_name="Integrated Results")
        except Exception as e:
            logger.error(f"Error reading Excel file {excel_path}: {e}")
            return None

    def _determine_discrepancy(self, row: pd.Series) -> str:
        """
        Determines the discrepancy level based on 'Step 2' results from all models.
        Matches the logic in ROBEvaluator.
        """
        step2_decisions = [row.get(f"{name} (Step 2)") for name in self.model_names]
        valid_decisions = [str(d).lower() for d in step2_decisions if pd.notna(d) and str(d).strip()]
        
        if len(set(valid_decisions)) <= 1:
            return "none"

        has_low = any("low" in d for d in valid_decisions)
        has_high = any("high" in d for d in valid_decisions)

        if has_low and has_high:
            return "major"  # Severe inconsistency (Orange/Red)
        else:
            return "minor"  # Minor inconsistency (Yellow)

    def _process_data(self, df: pd.DataFrame) -> dict:
        """
        Transforms the DataFrame into a JSON-serializable dictionary for the frontend.
        """
        primary_model_col = f"{self.model_names[0]} (Step 2)"
        if primary_model_col not in df.columns:
             raise ValueError(f"Primary model column '{primary_model_col}' not found in the Excel file. Please check config.json and the generated Excel file.")
        all_domains_in_df = df['Domain'].unique().tolist()
        
        ordered_domains = [d for d in self.core_domains if d in all_domains_in_df]
        if self.config['processing']['eval_optional_items']:
            ordered_domains += [d for d in self.optional_domains if d in all_domains_in_df]
        studies_data = {}
        for study_id, group in df.groupby('Study'):
            studies_data[study_id] = {}
            for _, row in group.iterrows():
                domain = row['Domain']
                if domain in ordered_domains:
                    studies_data[study_id][domain] = {
                        "result": row.get(primary_model_col, ""),
                        "discrepancy": self._determine_discrepancy(row)
                    }
        return {
            "studies": studies_data,
            "domains": ordered_domains,
            "core_domains": [d for d in self.core_domains if d in ordered_domains]
        }

    def _generate_html(self, data: dict) -> str:
        """
        Generates the full HTML content with embedded CSS and JavaScript.
        This is the final corrected version addressing layout and PDF export issues.
        """
        json_data = json.dumps(data, indent=2)
        # In f-strings, literal curly braces must be escaped by doubling them: {{ and }}
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ROB Assessment Visualization & Calibration</title>
    <!-- jsPDF and jsPDF-AutoTable for advanced PDF export -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf-autotable/3.8.2/jspdf.plugin.autotable.min.js"></script>
    
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.6; color: #333; background-color: #f8f9fa; margin: 0; padding: 20px;
        }}
        .container {{
            max-width: 95%; margin: auto; background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #0056b3; border-bottom: 2px solid #e9ecef; padding-bottom: 10px; font-size: 1.5em;
        }}
        .plot-instructions {{
            padding: 15px; background-color: #e9f7ff; border: 1px solid #b3e0ff; border-radius: 4px; margin: 20px 0; font-size: 0.9em;
        }}
        .plot-instructions code {{
            background-color: #dde1e3; padding: 2px 4px; border-radius: 3px; font-family: monospace;
        }}
        .controls {{
            margin-bottom: 20px; padding: 15px; background-color: #f0f0f0; border-radius: 5px; display: flex; align-items: center; gap: 20px;
        }}
        .controls label {{ font-weight: bold; margin-right: 5px; }}
        #export-pdf-btn {{
            background-color: #007bff; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; font-weight: bold; transition: background-color 0.2s;
        }}
        #export-pdf-btn:hover {{ background-color: #0056b3; }}
        #export-pdf-btn:disabled {{ background-color: #cccccc; cursor: not-allowed; }}
        .table-container {{ overflow-x: auto; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ border: 1px solid #dee2e6; padding: 8px; text-align: center; vertical-align: middle; }}
        th {{
            background-color: #f2f2f2; font-size: 12px; writing-mode: vertical-rl; text-orientation: mixed; white-space: nowrap; padding: 10px 5px;
        }}
        td.study-id-cell {{ 
            text-align: left; font-weight: bold; white-space: nowrap; background-color: #f8f9fa; cursor: text;
        }}
        td.study-id-cell:focus {{
            background-color: #e9ecef; outline: 2px solid #007bff;
        }}
        .circle {{
            width: 24px; height: 24px; border-radius: 50%; display: block;
            margin: 0 auto 5px auto;
            border: 1px solid rgba(0,0,0,0.2);
        }}
        .circle.dl {{ background-color: #196F3D; }}
        .circle.pl {{ background-color: #82E0AA; }}
        .circle.ph {{ background-color: #FADBD8; }}
        .circle.dh {{ background-color: #943126; }}
        .circle.na {{ background-color: #D5D8DC; }}
        td.conflict-minor {{ background-color: #FEF9E7; }}
        td.conflict-major {{ background-color: #F5B7B1; }}
        select {{
            border: 1px solid #ccc; border-radius: 4px; padding: 2px; font-size: 11px; width: 100%; max-width: 150px;
            display: block;
            margin: 0 auto;
        }}
        .summary-container, .hidden-column {{ display: none; }}
    </style>
</head>
<body>
    <div class="container" id="report-container">
        <h1>ROB Assessment Results: Calibration and Visualization Tool (Powered by SmartNMA)</h1>
        <div class="plot-instructions">
            <strong>Instruction for Calibration:</strong>
            <p style="margin: 5px 0 10px;">
                This traffic light plot visualizes the initial risk of bias assessments. Any cell with a colored background (pale yellow or orange) signifies a conflict where the LLM assessors did not agree. Your task is to resolve these conflicts.
            </p>
            <strong style="display: block; margin-bottom: 5px;">Your workflow:</strong>
            <ul style="margin: 0; padding-left: 20px;">
                <li><strong>Identify a Conflict:</strong> Locate a cell with a colored background on this page.</li>
                <li><strong>Consult the Evidence:</strong> Open the accompanying <strong>the generated Excel results file</strong>. Find the same study and domain to compare the different judgements, reasons, and supporting quotes from each model side-by-side.</li>
                <li><strong>Finalize the Decision:</strong> After your expert review of the evidence, return to this web page. Use the dropdown menu in the conflict cell to lock in your definitive assessment.</li>
                <li><strong>Confirm Resolution:</strong> Once a selection is made, the cell's background will clear, marking it as resolved.</li>
            </ul>
            <p style="margin-top: 10px;">
                The final PDF report can only be exported once every conflict in the current view (Core Items or All Items) has been resolved.
            </p>
        </div>
        <div class="controls">
            <div>
                <label for="item-filter">Show items:</label>
                <input type="radio" id="core-items-only" name="item-filter" value="core" checked>
                <label for="core-items-only">Core Items Only</label>
                <input type="radio" id="all-items" name="item-filter" value="all">
                <label for="all-items">All Items</label>
            </div>
            <button id="export-pdf-btn" disabled>Export to PDF</button>
        </div>
        <div class="table-container">
            <table id="rob-table"><thead id="rob-table-head"></thead><tbody id="rob-table-body"></tbody></table>
        </div>
    </div>
    <script>
        const assessmentData = {json_data};
        const RATING_MAP = {{
            "Definitely low": "dl", "Probably low": "pl",
            "Probably high": "ph", "Definitely high": "dh",
            "": "na", "Not available": "na", "Not reported": "na",
            "Need Manual Verification": "na"
        }};
        const COLOR_MAP_PDF = {{
            "dl": {{ name: "Definitely Low", color: "#196F3D" }},
            "pl": {{ name: "Probably Low", color: "#82E0AA" }},
            "ph": {{ name: "Probably High", color: "#FADBD8" }},
            "dh": {{ name: "Definitely High", color: "#943126" }},
            "na": {{ name: "Not Available / Not Reported", color: "#D5D8DC" }}
        }};
        
        const RATING_OPTIONS = ["Definitely low", "Probably low", "Probably high", "Definitely high"];
        const CONFLICT_PLACEHOLDER = "Need Manual Verification";
        
        function exportToPDF() {{
            const btn = document.getElementById('export-pdf-btn');
            btn.textContent = 'Generating...';
            btn.disabled = true;
            const {{ jsPDF }} = window.jspdf;
            const doc = new jsPDF({{ orientation: 'landscape' }});
            const FONT_SIZE = 10;
            const visibleDomains = Array.from(document.querySelectorAll('#rob-table-head th[data-domain]'))
                .filter(th => th.style.display !== 'none')
                .map(th => th.dataset.domain);
            
            const domainShortNames = {{}};
            const domainLegend = [];
            visibleDomains.forEach((domain, i) => {{
                const shortName = `Domain ${{i + 1}}`;
                domainShortNames[domain] = shortName;
                domainLegend.push(`${{shortName}}: ${{domain}}`);
            }});
            
            const tableHead = [['Study ID', ...visibleDomains.map(d => domainShortNames[d])]];
            const tableBody = [];
            
            document.querySelectorAll('#rob-table-body tr').forEach(row => {{
                if(row.style.display === 'none') return;
                
                const studyId = row.querySelector('.study-id-cell').textContent.trim();
                const rowData = [];
                const studyIdCellData = {{ content: studyId, styles: {{ halign: 'left' }} }};
                rowData.push(studyIdCellData);
                visibleDomains.forEach(domain => {{
                    const cell = row.querySelector(`td[data-domain="${{domain}}"]`);
                    const select = cell.querySelector('select');
                    const value = select.value;
                    const ratingClass = RATING_MAP[value] || 'na';
                    rowData.push(ratingClass);
                }});
                tableBody.push(rowData);
            }});
            doc.autoTable({{
                head: tableHead,
                body: tableBody,
                startY: 15,
                theme: 'grid',
                styles: {{ fontSize: FONT_SIZE, halign: 'center', valign: 'middle' }},
                headStyles: {{ fillColor: [242, 242, 242], textColor: 20, fontStyle: 'bold' }},
                didDrawCell: function (data) {{
                    if (data.section === 'body' && data.column.index > 0) {{
                        const ratingClass = data.cell.raw;
                        const colorInfo = COLOR_MAP_PDF[ratingClass];
                        if (colorInfo) {{
                            const circleX = data.cell.x + data.cell.width / 2;
                            const circleY = data.cell.y + data.cell.height / 2;
                            const radius = 3; 
                            doc.setFillColor(colorInfo.color);
                            doc.circle(circleX, circleY, radius, 'F');
                        }}
                        data.cell.text = [];
                    }}
                }}
            }});
            
            let finalY = doc.lastAutoTable.finalY + 10;
            
            doc.setFontSize(FONT_SIZE).setFont(undefined, 'bold');
            doc.text("Legend (Risk of Bias)", 14, finalY);
            finalY += 5;
            Object.values(COLOR_MAP_PDF).forEach(item => {{
                doc.setFillColor(item.color);
                doc.circle(16, finalY - 1.5, 2, 'F');
                doc.setFontSize(FONT_SIZE).setFont(undefined, 'normal');
                doc.text(item.name, 20, finalY);
                finalY += 5;
            }});
            finalY += 5;
            doc.setFontSize(FONT_SIZE).setFont(undefined, 'bold');
            doc.text("Domain Definitions", 14, finalY);
            finalY += 5;
            domainLegend.forEach(line => {{
                if (finalY > doc.internal.pageSize.height - 10) {{
                    doc.addPage();
                    finalY = 15;
                }}
                doc.setFontSize(FONT_SIZE).setFont(undefined, 'normal');
                doc.text(line, 14, finalY);
                finalY += 5;
            }});
            
            doc.save('rob_calibrated_report.pdf');
            btn.textContent = 'Export to PDF';
            checkExportButtonState();
        }}
        
        function checkExportButtonState() {{
            const btn = document.getElementById('export-pdf-btn');
            const showAll = document.getElementById('all-items').checked;
            let unresolvedConflicts = 0;
            const cells = document.querySelectorAll('#rob-table-body td[data-domain]');
            cells.forEach(cell => {{
                const isOptional = cell.dataset.domainType === 'optional';
                const parentColumn = document.querySelector(`#rob-table-head th[data-domain="${{cell.dataset.domain}}"]`);
                const isVisible = (showAll || !isOptional) && parentColumn.style.display !== 'none';
                
                if (isVisible && (cell.classList.contains('conflict-minor') || cell.classList.contains('conflict-major'))) {{
                    unresolvedConflicts++;
                }}
            }});
            
            if (unresolvedConflicts === 0) {{
                btn.disabled = false;
                btn.title = "Ready to export.";
            }} else {{
                btn.disabled = true;
                btn.title = `${{unresolvedConflicts}} unresolved conflict(s) remaining in the current view.`;
            }}
        }}
        document.addEventListener('DOMContentLoaded', function() {{
            const tableHead = document.getElementById('rob-table-head');
            const tableBody = document.getElementById('rob-table-body');
            
            function buildTable() {{
                tableHead.innerHTML = ''; tableBody.innerHTML = '';
                const headerRow = document.createElement('tr');
                headerRow.innerHTML = '<th>Study ID</th>';
                assessmentData.domains.forEach(domain => {{
                    const isCore = assessmentData.core_domains.includes(domain);
                    const th = document.createElement('th');
                    th.textContent = domain;
                    th.dataset.domain = domain;
                    th.dataset.domainType = isCore ? 'core' : 'optional';
                    headerRow.appendChild(th);
                }});
                tableHead.appendChild(headerRow);
                Object.keys(assessmentData.studies).sort().forEach(studyId => {{
                    const study = assessmentData.studies[studyId];
                    const row = document.createElement('tr');
                    const studyIdCell = document.createElement('td');
                    studyIdCell.className = 'study-id-cell';
                    studyIdCell.textContent = studyId;
                    studyIdCell.setAttribute('contenteditable', 'true');
                    studyIdCell.dataset.originalId = studyId;
                    row.appendChild(studyIdCell);
                    assessmentData.domains.forEach(domain => {{
                        const cell = document.createElement('td');
                        cell.dataset.studyId = studyId;
                        cell.dataset.domain = domain;
                        const isCore = assessmentData.core_domains.includes(domain);
                        cell.dataset.domainType = isCore ? 'core' : 'optional';
                        
                        const assessment = study[domain] || {{ result: "", discrepancy: "none" }};
                        const hasConflict = assessment.discrepancy !== "none";
                        
                        if (hasConflict) {{
                             cell.classList.add(assessment.discrepancy === 'minor' ? 'conflict-minor' : 'conflict-major');
                        }}
                        
                        const circle = document.createElement('div');
                        circle.className = 'circle';
                        
                        const select = document.createElement('select');
                        
                        if (hasConflict) {{
                            const placeholderOption = document.createElement('option');
                            placeholderOption.value = CONFLICT_PLACEHOLDER;
                            placeholderOption.textContent = CONFLICT_PLACEHOLDER;
                            placeholderOption.selected = true;
                            select.appendChild(placeholderOption);
                            circle.style.display = 'none';
                        }}
                        const initialResult = assessment.result;
                        const ratingClass = RATING_MAP[initialResult] || 'na';
                        circle.classList.add(ratingClass);
                        RATING_OPTIONS.forEach(opt => {{
                            const option = document.createElement('option');
                            option.value = opt; option.textContent = opt;
                            if (!hasConflict && opt === initialResult) {{
                                option.selected = true;
                            }}
                            select.appendChild(option);
                        }});
                        
                        cell.appendChild(circle);
                        cell.appendChild(select);
                        row.appendChild(cell);
                    }});
                    tableBody.appendChild(row);
                }});
            }}
            
            function handleFilterChange() {{
                const showAll = document.getElementById('all-items').checked;
                document.querySelectorAll('[data-domain-type="optional"]').forEach(el => {{
                    el.style.display = showAll ? '' : 'none';
                }});
                checkExportButtonState();
            }}
            
            tableBody.addEventListener('change', function(e) {{
                if (e.target.tagName === 'SELECT') {{
                    const cell = e.target.parentElement;
                    const newValue = e.target.value;
                    if (newValue !== CONFLICT_PLACEHOLDER) {{
                        cell.classList.remove('conflict-minor', 'conflict-major');
                        
                        const circle = cell.querySelector('.circle');
                        circle.style.display = 'block';
                        circle.className = 'circle';
                        circle.classList.add(RATING_MAP[newValue] || 'na');
                        
                        const placeholder = e.target.querySelector(`option[value="${{CONFLICT_PLACEHOLDER}}"]`);
                        if(placeholder) {{
                            e.target.removeChild(placeholder);
                        }}
                    }}
                    checkExportButtonState();
                }}
            }});
            tableBody.addEventListener('blur', function(e) {{
                if (e.target.classList.contains('study-id-cell')) {{
                    const cell = e.target;
                    const originalId = cell.dataset.originalId;
                    const newId = cell.textContent.trim();
                    if (newId && newId !== originalId) {{
                        if (assessmentData.studies[newId]) {{
                            alert(`Error: Study ID "${{newId}}" already exists. Please choose a unique ID.`);
                            cell.textContent = originalId;
                        }} else {{
                            assessmentData.studies[newId] = assessmentData.studies[originalId];
                            delete assessmentData.studies[originalId];
                            cell.dataset.originalId = newId;
                            cell.parentElement.querySelectorAll('td[data-study-id]').forEach(td => {{
                                td.dataset.studyId = newId;
                            }});
                            console.log(`Study ID changed from "${{originalId}}" to "${{newId}}"`);
                        }}
                    }} else if (!newId) {{
                        alert("Study ID cannot be empty.");
                        cell.textContent = originalId;
                    }}
                }}
            }}, true);
            
            document.getElementById('export-pdf-btn').addEventListener('click', exportToPDF);
            document.querySelectorAll('input[name="item-filter"]').forEach(radio => {{ radio.addEventListener('change', handleFilterChange); }});
            
            buildTable();
            handleFilterChange();
        }});
    </script>
</body>
</html>
"""