import markdown
import base64
import io
from PIL import Image

class ReportHelper:
    @staticmethod
    def convert_to_html(markdown_text, model_name):
        """
        Takes Markdown text and wraps it in a stylish HTML template.
        """
        raw_html = markdown.markdown(
            markdown_text,
            extensions=['fenced_code', 'nl2br', 'sane_lists']
        )

        template = f"""
        <style>
            .ai-report-box {{
                font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-left: 5px solid #dc3545; /* Error Red */
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
                <h3 class="ai-title">Artificial Intelligence Error Analysis</h3>
                <span class="ai-badge">{model_name}</span>
            </div>
            <div class="ai-content">
                {raw_html}
            </div>
        </div>
        """
        return template

    # ==========================================
    # 2. YENİ YAPI (GÖRSEL RAPOR) - Başlık Hizalaması Düzeltildi
    # ==========================================
    @staticmethod
    def create_visual_html_report(errors, figma_bytes, live_bytes, model_name):
        """
        JSON hatalarını alır, resimleri kırpar (CROP) ve Görsel HTML Kartları oluşturur.
        """
        img_figma = Image.open(io.BytesIO(figma_bytes))
        img_live = Image.open(io.BytesIO(live_bytes))
        
        f_width, f_height = img_figma.size
        l_width, l_height = img_live.size

        # Raporun Gövdesi
        html_cards = ""

        if not errors:
            html_cards = """
            <div style='padding:40px; text-align:center; background:#fff;'>
                <div style='font-size: 40px; margin-bottom: 10px;'>✅</div>
                <h3 style='color:#28a745; margin:0;'>Pixel Perfect! No visual issues found.</h3>
                <p style='color:#6c757d; margin-top:5px;'>The live implementation matches the design specs.</p>
            </div>
            """
        else:
            for err in errors:
                y_start = max(0.0, float(err.get('y_start', 0)) - 0.05)
                y_end = min(1.0, float(err.get('y_end', 0)) + 0.05)
                
                f_crop = img_figma.crop((0, int(f_height * y_start), f_width, int(f_height * y_end)))
                l_crop = img_live.crop((0, int(l_height * y_start), l_width, int(l_height * y_end)))

                def to_b64(img):
                    buf = io.BytesIO()
                    img.save(buf, format="PNG")
                    return base64.b64encode(buf.getvalue()).decode("utf-8")

                f_b64 = to_b64(f_crop)
                l_b64 = to_b64(l_crop)
                
                severity_color = "#dc3545" if err.get('severity') == 'High' else "#ffc107"

                html_cards += f"""
                <div class="ai-visual-card">
                    <div class="ai-visual-header">
                        <span class="ai-severity-dot" style="background-color: {severity_color};"></span>
                        <h3 class="ai-card-title">{err.get('title')}</h3>
                        <span class="ai-badge">{err.get('severity', 'Medium')}</span>
                    </div>
                    <div class="ai-visual-body">
                        <p class="ai-desc">{err.get('description')}</p>
                        <div class="ai-comparison-row">
                            <div class="ai-img-container">
                                <span class="ai-label">🎯 Figma Design (Expected)</span>
                                <img src="data:image/png;base64,{f_b64}" />
                            </div>
                            <div class="ai-img-container">
                                <span class="ai-label">💻 Live Site (Actual)</span>
                                <img src="data:image/png;base64,{l_b64}" />
                            </div>
                        </div>
                    </div>
                </div>
                """

        # --- DÜZELTME BURADA YAPILDI ---
        visual_template = f"""
        <style>
            .ai-visual-box {{ font-family: 'Segoe UI', sans-serif; background: #f8f9fa; border: 1px solid #ddd; border-radius: 8px; overflow: hidden; margin: 10px 0; }}
            
            /* Header Flexbox Ayarları - Düzeltildi */
            .ai-main-header {{ 
                background: #fff; 
                padding: 15px 20px; 
                border-bottom: 1px solid #ddd; 
                display: flex; 
                align-items: center; 
                gap: 15px; /* İkon, Başlık ve Badge arası boşluk */
            }}
            
            .ai-main-title {{ 
                color: #333; 
                font-weight: 700; 
                font-size: 18px;
                margin: 0; /* Margin sıfırlama önemli */
            }}
            
            .ai-model-badge {{ 
                background: #e2e6ea; 
                color: #555; 
                font-size: 11px; 
                padding: 4px 10px; 
                border-radius: 12px; 
                font-weight: bold; 
                text-transform: uppercase; 
                white-space: nowrap; /* Alt satıra düşmesini engeller */
            }}
            
            /* Visual Card Styles */
            .ai-visual-card {{ background: #fff; border: 1px solid #e9ecef; border-radius: 6px; margin: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
            .ai-visual-header {{ padding: 12px 20px; border-bottom: 1px solid #f1f1f1; display: flex; align-items: center; gap: 10px; }}
            .ai-severity-dot {{ width: 12px; height: 12px; border-radius: 50%; display: inline-block; }}
            .ai-card-title {{ margin: 0; font-size: 16px; color: #333; flex-grow: 1; }}
            .ai-badge {{ background-color: #e2e6ea; color: #495057; font-size: 11px; padding: 3px 8px; border-radius: 10px; font-weight: 600; }}
            
            .ai-visual-body {{ padding: 20px; }}
            .ai-desc {{ margin-top: 0; color: #555; line-height: 1.5; }}
            
            .ai-comparison-row {{ display: flex; gap: 15px; margin-top: 15px; }}
            .ai-img-container {{ flex: 1; text-align: center; }}
            .ai-img-container img {{ width: 100%; border: 1px solid #ddd; border-radius: 4px; padding: 2px; background: #fff; }}
            .ai-label {{ display: inline-block; font-size: 11px; font-weight: 700; color: #4f46e5; background-color: #eef2ff; padding: 4px 10px; border-radius: 6px; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.8px; border: 1px solid #e0e7ff; }}
        </style>
        
        <div class="ai-visual-box">
            <div class="ai-main-header">
                <span style="font-size: 24px;">📸</span>
                <h3 class="ai-main-title">AI Visual Comparison Report</h3>
                <span class="ai-model-badge">{model_name}</span>
            </div>
            {html_cards}
        </div>
        """
        return visual_template