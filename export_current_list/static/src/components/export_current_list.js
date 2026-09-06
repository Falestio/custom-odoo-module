/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { ListController } from "@web/views/list/list_controller";
import { useService } from "@web/core/utils/hooks";
import { _t } from "@web/core/l10n/translation";

patch(ListController.prototype, {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.notification = useService("notification");
    },


    get hasSelectedRecords() {
        return this.model.root.selection && this.model.root.selection.length > 0;
    },

    _getVisibleColumns() {
        const columns = this.props.archInfo?.columns || [];
        const fields = this.props.archInfo?.fields || this.model?.root?.fields || {};
        
        const visibleColumns = [];
        
        for (const column of columns) {
            if (column.type !== 'field') continue;
            
            if (column.widget === 'handle') continue;
            
            if (column.invisible === true || column.invisible === "True" || column.invisible === "1") continue;
            
            const fieldName = column.name;
            const fieldInfo = fields[fieldName];
            
            if (!fieldInfo) continue;
            
            visibleColumns.push({
                name: fieldName,
                string: column.string || fieldInfo.string || fieldName,
                type: fieldInfo.type,
                widget: column.widget,
            });
        }
        
        return visibleColumns;
    },

    _formatCellValue(record, column) {
        const fieldName = column.name;
        const value = record.data[fieldName];
        
        if (value === undefined || value === null || value === false) {
            if (column.type === 'boolean') {
                return _t("False");
            }
            return '';
        }
        
        switch (column.type) {
            case 'boolean':
                return value ? _t("True") : _t("False");
            
            case 'many2one':
                if (Array.isArray(value)) {
                    return value[1] || '';
                }
                return value.display_name || value.name || '';
            
            case 'many2many':
            case 'one2many':
                if (Array.isArray(value)) {
                    if (value.length === 0) return '';
                    if (value[0] && typeof value[0] === 'object') {
                        return value.map(v => v.display_name || v.name || '').join(', ');
                    }
                    return `${value.length} record(s)`;
                }
                if (value.records) {
                    return value.records.map(r => r.data.display_name || r.data.name || '').join(', ');
                }
                return '';
            
            case 'date':
            case 'datetime':
                if (value) {
                    if (typeof value === 'object' && value.toFormat) {
                        return column.type === 'date' 
                            ? value.toFormat('yyyy-MM-dd')
                            : value.toFormat('yyyy-MM-dd HH:mm:ss');
                    }
                    return String(value);
                }
                return '';
            
            case 'selection':
                const fieldInfo = this.model.root.fields[fieldName];
                if (fieldInfo && fieldInfo.selection) {
                    const selection = fieldInfo.selection.find(s => s[0] === value);
                    return selection ? selection[1] : value;
                }
                return value;
            
            case 'integer':
            case 'float':
            case 'monetary':
                return typeof value === 'number' ? value : parseFloat(value) || 0;
            
            case 'html':
                if (typeof value === 'string') {
                    let text = value;
                    // Replace <br>, <br/>, <br /> with newline
                    text = text.replace(/<br\s*\/?>/gi, '\n');
                    // Replace closing </p>, </div>, </li> with newline
                    text = text.replace(/<\/(?:p|div|li|tr)>/gi, '\n');
                    // Replace <p>, <div>, <li>, <tr> opening tags with nothing (newline handled by closing tag)
                    text = text.replace(/<(?:p|div|li|tr)[^>]*>/gi, '');
                    
                    // Remove all other HTML tags
                    const div = document.createElement('div');
                    div.innerHTML = text;
                    text = div.textContent || div.innerText || '';
                    
                    // Clean up multiple consecutive newlines (max 2)
                    text = text.replace(/\n{3,}/g, '\n\n');
                    // Trim each line but preserve newlines
                    text = text.split('\n').map(line => line.trim()).join('\n');
                    return text.trim();
                }
                return value;
            
            default:
                return String(value);
        }
    },

    async onExportCurrentList() {
        const selectedRecords = this.model.root.selection;
        const totalCount = this.model.root.count;
        const limit = this.model.root.limit || 80;
        
        const isDomainSelected = this.model.root.isDomainSelected || 
                                 this.model.root.selectDomain ||
                                 (selectedRecords.length === limit && totalCount > limit);
        
        if (!selectedRecords || selectedRecords.length === 0) {
            this.notification.add(_t("Please select at least one record to export."), {
                type: 'warning',
            });
            return;
        }
        
        const columns = this._getVisibleColumns();
        
        if (columns.length === 0) {
            this.notification.add(_t("No columns available to export."), {
                type: 'warning',
            });
            return;
        }
        
        const headers = columns.map(col => col.string);
        const fieldNames = columns.map(col => col.name);
        
        const domain = this.model.root.domain || [];
        const context = this.model.root.context || {};
        
        const selectedIds = selectedRecords.map(record => record.resId);
        
        const exportData = {
            model: this.props.resModel,
            headers: headers,
            field_names: fieldNames,
            domain: domain,
            context: context,
            selected_ids: selectedIds,
            is_domain_selected: isDomainSelected,
            total_count: totalCount,
        };
        
        this._submitExportForm(exportData, isDomainSelected ? totalCount : selectedRecords.length);
    },
    
  
    _submitExportForm(exportData, recordCount) {
        const token = Date.now().toString();
        
        const url = '/web/export/current_list_xls';
        
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = url;
        form.target = '_blank';
        
        const dataInput = document.createElement('input');
        dataInput.type = 'hidden';
        dataInput.name = 'data';
        dataInput.value = JSON.stringify(exportData);
        form.appendChild(dataInput);
        
        const tokenInput = document.createElement('input');
        tokenInput.type = 'hidden';
        tokenInput.name = 'token';
        tokenInput.value = token;
        form.appendChild(tokenInput);
        
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrf_token';
        csrfInput.value = odoo.csrf_token;
        form.appendChild(csrfInput);
        
        document.body.appendChild(form);
        form.submit();
        document.body.removeChild(form);
    },
});
