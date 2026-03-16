"""
质量报告生成器 - 企业级实现
生成美观的质量报告
"""

from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timezone
import json

from meta_agent.core.logging import get_logger
from tools.quality_gate.quality_gate import GateResult, GateStatus

logger = get_logger(__name__)


@dataclass
class ReportFormat:
    """报告格式"""
    JSON = "json"
    HTML = "html"
    MARKDOWN = "markdown"


class QualityReporter:
    """质量报告生成器"""
    
    def __init__(self, output_dir: Path = Path("./reports/quality")):
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate(
        self,
        result: GateResult,
        formats: Optional[List[str]] = None,
    ) -> Dict[str, Path]:
        """生成报告"""
        if formats is None:
            formats = [ReportFormat.JSON, ReportFormat.HTML, ReportFormat.MARKDOWN]
        
        generated_files: Dict[str, Path] = {}
        
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        
        if ReportFormat.JSON in formats:
            file_path = self.output_dir / f"quality_report_{timestamp}.json"
            self._generate_json(result, file_path)
            generated_files[ReportFormat.JSON] = file_path
        
        if ReportFormat.HTML in formats:
            file_path = self.output_dir / f"quality_report_{timestamp}.html"
            self._generate_html(result, file_path)
            generated_files[ReportFormat.HTML] = file_path
        
        if ReportFormat.MARKDOWN in formats:
            file_path = self.output_dir / f"quality_report_{timestamp}.md"
            self._generate_markdown(result, file_path)
            generated_files[ReportFormat.MARKDOWN] = file_path
        
        return generated_files
    
    def _generate_json(self, result: GateResult, file_path: Path) -> None:
        """生成JSON报告"""
        data = {
            "timestamp": result.timestamp,
            "duration_seconds": result.duration_seconds,
            "status": result.status.name,
            "overall_score": result.score.overall_score,
            "category_scores": {
                cat.name: score for cat, score in result.score.category_scores.items()
            },
            "passed": result.score.passed,
            "recommendations": result.score.recommendations,
            "rule_results": result.rule_results,
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON报告已生成: {file_path}")
    
    def _generate_html(self, result: GateResult, file_path: Path) -> None:
        """生成HTML报告"""
        status_color = {
            GateStatus.PASSED: "#4CAF50",
            GateStatus.FAILED: "#F44336",
            GateStatus.WARNING: "#FF9800",
            GateStatus.SKIPPED: "#9E9E9E",
        }
        
        table_rows = ''.join([
            f'<tr><td>{cat.name}</td><td>{score:.1%}</td>'
            f'<td class="{"pass" if score >= 0.8 else "fail"}">'
            f'{"通过" if score >= 0.8 else "未通过"}</td></tr>'
            for cat, score in result.score.category_scores.items()
        ])
        
        rec_items = ''.join([f'<li>{rec}</li>' for rec in result.score.recommendations])
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MetaAgent 质量报告</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: {status_color.get(result.status, '#9E9E9E')}; 
                  color: white; padding: 20px; border-radius: 5px; }}
        .score {{ font-size: 48px; font-weight: bold; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .pass {{ color: #4CAF50; }}
        .fail {{ color: #F44336; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>MetaAgent 质量报告</h1>
        <div class="score">{result.score.overall_score:.1%}</div>
        <div>状态: {result.status.name}</div>
        <div>耗时: {result.duration_seconds:.2f}s</div>
    </div>
    
    <div class="section">
        <h2>分类评分</h2>
        <table>
            <tr><th>类别</th><th>评分</th><th>状态</th></tr>
            {table_rows}
        </table>
    </div>
    
    <div class="section">
        <h2>改进建议</h2>
        <ul>
            {rec_items}
        </ul>
    </div>
</body>
</html>
        """
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        logger.info(f"HTML报告已生成: {file_path}")
    
    def _generate_markdown(self, result: GateResult, file_path: Path) -> None:
        """生成Markdown报告"""
        lines = []
        lines.append("# MetaAgent 质量报告")
        lines.append("")
        lines.append("## 概览")
        lines.append("")
        lines.append(f"- **状态**: {result.status.name}")
        lines.append(f"- **综合评分**: {result.score.overall_score:.1%}")
        lines.append(f"- **检查耗时**: {result.duration_seconds:.2f}s")
        lines.append("")
        lines.append("## 分类评分")
        lines.append("")
        lines.append("| 类别 | 评分 | 状态 |")
        lines.append("|------|------|------|")
        for cat, score in result.score.category_scores.items():
            status_text = "通过" if score >= 0.8 else "未通过"
            lines.append(f"| {cat.name} | {score:.1%} | {status_text} |")
        lines.append("")
        lines.append("## 改进建议")
        lines.append("")
        for rec in result.score.recommendations:
            lines.append(f"- {rec}")
        lines.append("")
        lines.append("---")
        lines.append(f"生成时间: {datetime.fromtimestamp(result.timestamp).isoformat()}")
        
        md = "\n".join(lines)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(md)
        
        logger.info(f"Markdown报告已生成: {file_path}")
