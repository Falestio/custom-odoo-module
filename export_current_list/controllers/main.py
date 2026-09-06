# -*- coding: utf-8 -*-
import json
import io
from odoo import http
from odoo.http import request, content_disposition


class ExportCurrentListController(http.Controller):
    
    def _format_value_for_export(self, record, field_name, field_type):
        """Format field value for Excel export"""
        import re
        from html import unescape
        
        value = record[field_name]
        
        if value is None or value is False:
            return '' if field_type != 'boolean' else False
        
        if field_type in ('many2one',):
            return value.display_name if hasattr(value, 'display_name') else str(value)
        elif field_type in ('many2many', 'one2many'):
            return ', '.join(rec.display_name for rec in value) if value else ''
        elif field_type == 'selection':
            field_obj = record._fields[field_name]
            selection = field_obj.selection
            if callable(selection):
                selection = selection(record.env[record._name])
            selection_dict = dict(selection) if selection else {}
            return selection_dict.get(value, value)
        elif field_type == 'boolean':
            return value
        elif field_type == 'html':
            # Strip HTML tags and decode HTML entities, preserve new lines
            if isinstance(value, str):
                text = value
                # Replace <br>, <br/>, <br /> with newline
                text = re.sub(r'<br\s*/?>', '\n', text, flags=re.IGNORECASE)
                # Replace closing </p>, </div>, </li>, </tr> with newline
                text = re.sub(r'</(?:p|div|li|tr)>', '\n', text, flags=re.IGNORECASE)
                # Replace opening <p>, <div>, <li>, <tr> tags (newline handled by closing tag)
                text = re.sub(r'<(?:p|div|li|tr)[^>]*>', '', text, flags=re.IGNORECASE)
                
                # Remove all other HTML tags
                text = re.sub(r'<[^>]+>', '', text)
                text = unescape(text)
                
                # Clean up multiple consecutive newlines (max 2)
                text = re.sub(r'\n{3,}', '\n\n', text)
                # Trim each line but preserve newlines
                text = '\n'.join(line.strip() for line in text.split('\n'))
                return text.strip()
            return value
        else:
            return value
    
    @http.route('/web/export/current_list_xls', type='http', auth='user')
    def export_current_list_xls(self, data, token):
        try:
            import xlsxwriter
        except ImportError:
            raise Exception("xlsxwriter library is required. Install it with: pip install xlsxwriter")
        
        data = json.loads(data)
        model_name = data.get('model', 'export')
        headers = data.get('headers', [])
        domain = data.get('domain', [])
        context = data.get('context', {})
        field_names = data.get('field_names', [])
        selected_ids = data.get('selected_ids', [])
        is_domain_selected = data.get('is_domain_selected', False)
        
        Model = request.env[model_name].with_context(**context)
        
        if is_domain_selected:
            records = Model.search(domain)
        elif selected_ids:
            records = Model.browse(selected_ids)
        else:
            records = Model.search(domain)
        
        field_types = {fname: Model._fields[fname].type for fname in field_names if fname in Model._fields}
        
        rows = []
        for record in records:
            row = []
            for field_name in field_names:
                field_type = field_types.get(field_name, 'char')
                cell_value = self._format_value_for_export(record, field_name, field_type)
                row.append(cell_value)
            rows.append(row)
        
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        worksheet = workbook.add_worksheet('Data')
        
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
        })
        
        cell_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'text_wrap': True,
        })
        
        number_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'num_format': '#,##0.00',
            'text_wrap': True,
        })
        
        date_format = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'num_format': 'yyyy-mm-dd',
        })
        
        for col, header in enumerate(headers):
            worksheet.write(0, col, header, header_format)
            worksheet.set_column(col, col, max(len(str(header)) + 2, 12))
        
        for row_idx, row in enumerate(rows, start=1):
            for col_idx, cell_value in enumerate(row):
                if isinstance(cell_value, (int, float)) and not isinstance(cell_value, bool):
                    worksheet.write_number(row_idx, col_idx, cell_value, number_format)
                else:
                    worksheet.write(row_idx, col_idx, cell_value if cell_value else '', cell_format)
        
        for col_idx, header in enumerate(headers):
            max_len = len(str(header))
            for row in rows:
                if col_idx < len(row) and row[col_idx]:
                    max_len = max(max_len, len(str(row[col_idx])))
            worksheet.set_column(col_idx, col_idx, min(max_len + 2, 50))
        
        workbook.close()
        output.seek(0)
        
        filename = f"{model_name.replace('.', '_')}_export.xlsx"
        
        response = request.make_response(
            output.read(),
            headers=[
                ('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'),
                ('Content-Disposition', content_disposition(filename)),
            ],
            cookies={'fileToken': token}
        )
        
        return response
