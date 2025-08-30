document.addEventListener('DOMContentLoaded', init);

let allReportData = {};
let currentData = null;
let currentReportKey = null;

const editableColumns = [
    "ROB", "Reason_for_ROB", "Inconsistency", "Reason_for_Inconsistency",
    "Indirectness", "Reason_for_Indirectness", "Publication_bias", "Reason_for_Publication_bias",
    "Intransitivity", "Reason_for_Intransitivity", "Incoherence", "Reason_for_Incoherence",
    "Imprecision", "Reason_for_Imprecision"
];

const calculatedColumns = [
    "Direct_rating_without_imprecision", 
    "Certainty_of_evidence_for_arm1", // Added
    "Certainty_of_evidence_for_arm2", // Added
    "Indirect_rating_without_imprecision",
    "Higher_rating_of_direct_and_indirect_without_imprecision", 
    "Evidence_type_for_final_rating",
    "Final_rating", 
    "Final_rating_reason"
];

const ratingOptions = {
    "ROB": ["Not serious", "Serious", "Very serious"], "Inconsistency": ["Not serious", "Serious", "Very serious"],
    "Indirectness": ["Not serious", "Serious", "Very serious"], "Publication_bias": ["Not serious", "Serious", "Very serious", "Undetected"],
    "Intransitivity": ["Not serious", "Serious", "Very serious"], "Incoherence": ["Not serious", "Serious", "Very serious"],
    "Imprecision": ["Not serious", "Serious", "Very serious", "Extremely serious"]
};

function init() {
    if (window.EMBEDDED_DATA && typeof window.EMBEDDED_DATA === 'object' && Object.keys(window.EMBEDDED_DATA).length > 0) {
        allReportData = window.EMBEDDED_DATA;
        const outcomeSelector = document.getElementById('outcome-selector');
        const saveButton = document.getElementById('save-button');
        
        populateSelector(Object.keys(allReportData));
        outcomeSelector.addEventListener('change', loadSelectedData);
        saveButton.addEventListener('click', saveModifiedData);
        loadSelectedData();
    } else {
        const container = document.getElementById('table-container');
        container.innerHTML = `<p style="color: red; font-weight: bold;">Error: No data was embedded. Please run 'run.py' again.</p>`;
    }
}

function populateSelector(keys) {
    const selector = document.getElementById('outcome-selector');
    selector.innerHTML = '';
    keys.forEach(key => {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = key;
        selector.appendChild(option);
    });
}

function loadSelectedData() {
    const selector = document.getElementById('outcome-selector');
    currentReportKey = selector.value;
    const selectedReport = allReportData[currentReportKey];
    currentData = JSON.parse(JSON.stringify(selectedReport.data)); // Deep copy
    renderTable(currentData);
    updateDownloadLink(selectedReport.excel_path);
}

function handleInputChange(event) {
    const { rowIndex, column } = event.target.dataset;
    currentData[rowIndex][column] = event.target.value;
    
    // Trigger the live calculation cascade
    currentData = updateAllCalculations(currentData);
    
    // Update only the calculated cells in the UI for performance
    updateRenderedTable(currentData);
}

function updateRenderedTable(data) {
    const tableBody = document.querySelector("#grade-table tbody");
    if (!tableBody) return;

    data.forEach((row, rowIndex) => {
        calculatedColumns.forEach(colName => {
            const cell = tableBody.querySelector(`tr[data-row-index='${rowIndex}'] td[data-column='${colName}']`);
            if (cell) {
                cell.textContent = row[colName] === null ? "" : row[colName];
            }
        });
    });
}

function renderTable(data) {
    const container = document.getElementById('table-container');
    if (!data || data.length === 0) {
        container.innerHTML = '<p>No data to display.</p>';
        return;
    }
    const table = document.createElement('table');
    table.id = "grade-table";
    const thead = document.createElement('thead');
    const tbody = document.createElement('tbody');
    
    const headers = Object.keys(data[0]);
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.replace(/_/g, ' ');
        if (header.toLowerCase().includes('reason')) th.classList.add('reason-col');
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    data.forEach((row, rowIndex) => {
        const tr = document.createElement('tr');
        tr.dataset.rowIndex = rowIndex;
        headers.forEach(header => {
            const td = document.createElement('td');
            td.dataset.column = header;
            const value = row[header] === null ? "" : row[header];
            if (editableColumns.includes(header)) {
                td.classList.add('editable-cell');
                const cellWrapper = document.createElement('div');
                cellWrapper.className = 'cell-content-wrapper';
                let inputElement;
                if (ratingOptions[header]) {
                    const select = document.createElement('select');
                    select.dataset.rowIndex = rowIndex;
                    select.dataset.column = header;
                    ratingOptions[header].forEach(opt => {
                        const option = document.createElement('option');
                        option.value = opt; option.textContent = opt;
                        if (opt === value) option.selected = true;
                        select.appendChild(option);
                    });
                    select.addEventListener('change', handleInputChange);
                    inputElement = select;
                } else {
                    const textarea = document.createElement('textarea');
                    textarea.dataset.rowIndex = rowIndex; textarea.dataset.column = header;
                    textarea.value = value;
                    textarea.addEventListener('input', handleInputChange);
                    inputElement = textarea;
                }
                cellWrapper.appendChild(inputElement);
                td.appendChild(cellWrapper);
            } else {
                td.textContent = value;
                if (calculatedColumns.includes(header)) {
                    td.classList.add('calculated-cell');
                }
            }
           
            const addTooltipHint = (targetTd, hintText) => {
                targetTd.classList.add('has-hint');
                const wrapper = targetTd.querySelector('.cell-content-wrapper');
                if (!wrapper) return;
                const tooltipContainer = document.createElement('div');
                tooltipContainer.className = 'tooltip-container';
                const trigger = document.createElement('span');
                trigger.className = 'tooltip-trigger';
                trigger.textContent = '?';
                const tooltip = document.createElement('div');
                tooltip.className = 'tooltip-text';
                tooltip.innerHTML = hintText;
                tooltipContainer.appendChild(trigger);
                tooltipContainer.appendChild(tooltip);
                wrapper.appendChild(tooltipContainer);
            };
            if (header === 'Imprecision' && row.Inconsistency && row.Inconsistency !== 'Not serious') {
                const hintText = `<strong>Note:</strong> Significant inconsistency often contributes to wider confidence intervals, a key factor in imprecision. To avoid double-counting uncertainty, consider reducing or omitting the downgrade for imprecision when inconsistency is already rated as serious.`;
                addTooltipHint(td, hintText);
            }
            if (header === 'Intransitivity' && row.Incoherence && row.Incoherence !== 'Not serious') {
                const hintText = `<strong>Note:</strong> Intransitivity is a primary conceptual reason for statistical incoherence. Since the evidence is already downgraded for incoherence, consider omitting a separate downgrade for intransitivity unless distinct concerns warrant it.`;
                addTooltipHint(td, hintText);
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    container.innerHTML = '';
    container.appendChild(table);
}

function updateDownloadLink(path) {
    const link = document.getElementById('download-link');
    link.href = path;
    link.download = path.split('/').pop();
}

function saveModifiedData() {
    if (!currentData) { alert("No data to save."); return; }
    const headers = Object.keys(currentData[0]);
    const csvRows = [headers.join(',')];
    currentData.forEach(row => {
        const values = headers.map(header => {
            let cell = row[header] === null ? '' : row[header].toString();
            if (cell.includes(',')) cell = `"${cell.replace(/"/g, '""')}"`;
            return cell;
        });
        csvRows.push(values.join(','));
    });
    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `${currentReportKey.replace(/[\s()]/g, '_').replace(/__+/g, '_')}_modified.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
