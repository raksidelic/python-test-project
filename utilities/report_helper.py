import markdown

class ReportHelper:
    @staticmethod
    def convert_to_html(markdown_text, model_name):
        """
        Markdown metni alır, şık bir HTML şablonuna giydirir.
        """
        # 1. Markdown -> Saf HTML Dönüşümü
        raw_html = markdown.markdown(
            markdown_text,
            extensions=['fenced_code', 'nl2br', 'sane_lists']
        )

        # 2. HTML Şablonu (CSS + Yapı)
        # Bu kısım logic'ten izole edildiği için istediğin kadar süsleyebilirsin.
        template = f"""
        <style>
            .ai-report-box {{
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-left: 5px solid #dc3545; /* Hata Kırmızısı */
                border-radius: 6px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.05);
                margin: 10px 0;
                overflow: hidden;
            }}
            .ai-header {{
                background-color: #fff;
                padding: 12px 20px;
                border-bottom: 1px solid #e9ecef;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .ai-title {{
                color: #dc3545;
                font-weight: 700;
                font-size: 16px;
                margin: 0;
            }}
            .ai-badge {{
                background-color: #e2e6ea;
                color: #495057;
                font-size: 11px;
                padding: 3px 8px;
                border-radius: 10px;
                font-weight: 600;
                text-transform: uppercase;
            }}
            .ai-content {{
                padding: 20px;
                color: #212529;
                line-height: 1.6;
                font-size: 14px;
            }}
            /* Kod Blokları */
            pre {{
                background: #2b2b2b;
                color: #f8f8f2;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
                font-family: 'Consolas', 'Monaco', monospace;
            }}
            code {{
                font-family: 'Consolas', 'Monaco', monospace;
                background-color: #e9ecef;
                padding: 2px 4px;
                border-radius: 3px;
                color: #c7254e;
            }}
            pre code {{
                background-color: transparent;
                color: inherit;
                padding: 0;
            }}
            ul {{ padding-left: 20px; margin: 0; }}
            li {{ margin-bottom: 8px; }}
        </style>
        
        <div class="ai-report-box">
            <div class="ai-header">
                <span style="font-size: 20px;">🤖</span>
                <h3 class="ai-title">Yapay Zeka Hata Analizi</h3>
                <span class="ai-badge">{model_name}</span>
            </div>
            <div class="ai-content">
                {raw_html}
            </div>
        </div>
        """
        return template